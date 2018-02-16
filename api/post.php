<?php
    include('_functions.php');

    function kill($msg) {
        die(json_encode(array('error' => $msg)));
    }

    function CheckNetObj($post) {
        $qry = "SELECT CASE WHEN $1::TEXT IN (SELECT DISTINCT(netobj) FROM tim_netobj_keys) THEN TRUE ELSE FALSE END netobjfound";
        $netobj = NULL;
        if (array_key_exists("netobj", $post)) {
            $netobj = $post["netobj"];
        } else {
            kill("Missing required key 'netobj'");
        }
        $con = ConnectToDB();
        $req = pg_query_params($qry, array($netobj)) or kill('DB Error');
        if (pg_fetch_result($req, 0, 'netobjfound') == 't') {
            return $netobj;
        } else {
            kill("Invalid netobj '" . $netobj . "'");
        }
    }

    function CheckNetObjKeys($post) {
        // Implicit valid "netobj" for $post
        $netobj = $post["netobj"];
        $qry = "SELECT field FROM tim_netobj_keys WHERE netobj = $1::TEXT";
        if (array_key_exists("keys", $post)) {
            if (is_array($post["keys"])) {
                
            } else {
                kill("Invalid value for key 'keys'");
            }
        } else {
            kill("Missing required key 'keys'");
        }
        $req = pg_query_params($qry, array($netobj)) or kill('DB Error');
        $payload = pg_fetch_all_columns($req, 0);
        $keys = array();
        foreach($payload as $_ => $key) {
            if (array_key_exists($key, $post["keys"])) {
                $value = $post["keys"][$key];
                $keys[$key] = $value;
            } else {
                kill("Missing required netobj key '" . $key . "'");
            }
        }
        return $keys;
    }

    function GetNetObjNetFields($post) {
        $fields = NULL;
        if (array_key_exists("netfields", $post)) {
            if (is_array($post["netfields"])) {
                $fields = $post["netfields"];
            } else {
                $fields = array($post["netfields"]);
            }
        } else {
            // NOOP - OK
            return NULL;
        }
        return $fields;
    }

    function GetNetObjDatFields($post) {
        $tod = NULL;
        $fields = NULL;
        if (array_key_exists("datfields", $post)) {
            if (array_key_exists("tod", $post["datfields"])) {
                if (is_array($post["datfields"]["tod"])) {
                    $tod = $post["datfields"]["tod"];
                } else {
                    $tod = array($post["datfields"]["tod"]);
                }
            } else {
                // Imply all TODs
                $tod = array("AM", "MD", "PM", "NT");
            }
            if (array_key_exists("fields", $post["datfields"])) {
                if (is_array($post["datfields"]["fields"])) {
                    $fields = $post["datfields"]["fields"];
                } else {
                    $fields = array($post["datfields"]["fields"]);
                }
            } else {
                kill("Missing required datfields key 'fields'");
            }
        } else {
            // NOOP - OK
            return NULL;
        }
        return array("tod" => $tod, "fields" => $fields);
    }

    function CheckTableExists($tblname) {
        $qry = "SELECT CASE WHEN $1::TEXT IN (SELECT DISTINCT(table_name::TEXT) FROM meta) THEN TRUE ELSE FALSE END tblfound";
        $con = ConnectToDB();
        $req = pg_query_params($qry, array($tblname)) or kill ('DB Error');
        return (pg_fetch_result($req, 0, 'tblfound') == 't');
    }
    function RiskyBuildExecuteQuery($tblname, $keyfields, $tod = NULL) {
        if (!CheckTableExists($tblname)) {
            return array();
        }
        $con = ConnectToDB();
        $qry = "SELECT row_to_json(t) json FROM " . $tblname . " t WHERE ";
        $qry_param = array();
        $i = 1;
        foreach($keyfields as $key => $value) {
            if ($i > 1) {
                $qry .= "AND ";
            }
            $qry .= $key . " = $" . (string) $i . " ";
            // lol this language
            $qry_param[] = $value;
            $i++;
        }
        if ($tod) {
            $qry .= "AND tod = ANY(" . pg_toTextArray($con, $tod) . ")";
        }
        $req = pg_query_params($qry, $qry_param) or kill('DB Error');
        // ... pg_fetch_assoc craps string values regardless of pgsql's dtypes
        // so fuck it, we'll use GLORIOUS POSTGRES to return a JSON
        $payload = pg_fetch_all($req);
        if ($tod) {
            return _ProcessTODPayload($payload);
        } else {
            return _ProcessSinglePayload($payload);
        }
    }
    function _ProcessSinglePayload($payload) {
        if (count($payload) > 0) {
            return json_decode($payload[0]["json"], true);
        } else {
            return array();
        };
    }
    function _ProcessTODPayload($payload) {
        $retval = array();
        foreach($payload as $jsonwrapper) {
            $enc_json = $jsonwrapper["json"];
            $retval[] = json_decode($enc_json, true);
        }
        return $retval;
    }

    ////

    if (strcasecmp($_SERVER['REQUEST_METHOD'], 'GET') == 0) {
        kill('GET');
    } else if (strcasecmp($_SERVER['REQUEST_METHOD'], 'POST') == 0) {
        $post_payload = trim(file_get_contents("php://input"));
        try {
            $post = json_decode($post_payload, true);
        } catch (Exception $e) {
            kill("Invalid POST JSON");
        }
    } else {
        kill(":(");
    }

    ////

    $netobj = CheckNetObj($post);
    $netobjkeys = CheckNetObjKeys($post);
    $netfields = GetNetObjNetFields($post);
    $datfields = GetNetObjDatFields($post);

    if (is_null($netfields) && is_null($datfields)) {
        kill("Empty request - No fields to return");
    }

    $netpayload = array();
    if (!is_null($netfields)) {
        $payload = RiskyBuildExecuteQuery("net_" . $netobj, $netobjkeys);
        foreach($netfields as $field) {
            if (array_key_exists($field, $payload)) {
                $netpayload[$field] = $payload[$field];
            }
        }
    }

    $datpayload = array();
    if (!is_null($datfields)) {
        $payload = RiskyBuildExecuteQuery("dat_" . $netobj, $netobjkeys, $datfields["tod"]);
        foreach($payload as $record) {
            $tod = $record["tod"];
            foreach($datfields["fields"] as $field) {
                if (array_key_exists($field, $record)) {
                    if (!array_key_exists($tod, $datpayload)) {
                        $datpayload[$tod] = array();
                    }
                    $datpayload[$tod][$field] = $record[$field];
                }
            }
        }
    }

    ////

    die(json_encode(array(
        'netobj' => $netobj,
        'netobjkeys' => $netobjkeys,
        'netfields' => $netfields,
        'datfields' => $datfields,
        'netpayload' => $netpayload,
        'datpayload' => $datpayload
    )));

?>
