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
            return NULL;
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
        $payload = pg_fetch_assoc($req);
        $keys = array();
        foreach($payload as $_ => $key) {
            if (array_key_exists($key, $post["keys"])) {
                $value = $post["keys"][$key];
                $keys[$key] = $value;
            } else {
                die("Missing required netobj key '" . $key . "'");
            }
        }
        return $keys;
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
    if ($netobj) {
        
    } else {
        kill("Invalid netobj '" . $post["netobj"] . "'");
    }

    ////

    $netobjkeys = CheckNetObjKeys($post);

    ////

    die(json_encode(array(
        'netobj' => $netobj,
        'netobjkeys' => $netobjkeys
    )));

?>
