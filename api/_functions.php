<?php
    include('_credentials.php');

    function ConnectToDB() {
        global $PGSQL_CONNECTION_STRING;
        $con = pg_connect($PGSQL_CONNECTION_STRING) or
            die('Unable to connect: ' . pg_last_error());
        return $con;
    }
    function pg_toIntArray($array) {
        // SQL Injection warning - should be relatively more safer with int type casting
        $pgarray = "ARRAY[";
        $n = count($array);
        for ($i = 0; $i < $n - 1; $i++) {
            $pgarray .= (int) $array[$i] . ',';
        }
        return $pgarray . (int) $array[$n - 1] . "]";
    }
    function pg_toTextArray($con, $array) {
        $pgarray = "ARRAY['";
        $n = count($array);
        for ($i = 0; $i < $n - 1; $i++) {
            $pgarray .= pg_escape_string($con, $array[$i]) . "','";
        }
        return $pgarray . pg_escape_string($con, $array[$n - 1]) . "']";
    }

    function _parseAttribute($att, $array, $ignoreerror = FALSE) {
        if (array_key_exists($att, $array)) {
            return urldecode($array[$att]);
        } else {
            if ($ignoreerror) {
                return True;
            } else {
                die('Missing parameter');
            }
        }
    }
    function _parseAttributes($att, $array) {
        $att_cnt_key = $att . 'n';
        $att_cnt = (int) _parseAttribute($att_cnt_key, $array);
        $atts = array();
        for ($i = 0; $i < $att_cnt; $i++) {
            $att_key = $att . $i;
            array_push($atts, urldecode($array[$att_key]));
        }
        return $atts;
    }

    function ParseAttributes($get) {
        $atts = array();
        if (array_key_exists("an", $get)) {
            $n = (int) $get["an"];
            for ($i = 0; $i < $n; $i++) {
                $k = "a" . $i;
                array_push($atts, urldecode($get[$k]));
            }
        }
        return $atts;
    }

    function ParseType($get) {
        if (array_key_exists("t", $get)) {
            return $get["t"];
        } else {
            die('Missing type parameter');
        }
    }
    function ParseGeomType($get) {
        if (array_key_exists("g", $get)) {
            return $get["g"];
        } else {
            die('Missing type parameter');
        }
    }

    function GetData($netobj, $param) {
        switch (ParseType($param)) {
            case 'g':
                return GetGeoJSON($netobj, $param);
                break;
            case 'a':
                return GetAttributesJSON($netobj, $param);
                break;
            case 't':
                return GetTemporalAttributesJSON($netobj, $param);
                break;
            default:
                die("Invalid Type");
                break;
        }
    }

    function GetGeoJSON($netobj, $param) {
        $qry = "SELECT tim_gfx_netobj($1,$2)";
        switch (ParseGeomType($param)) {
            case "p":
                $geomtype = "wktloc";
                break;
            case "l":
                $geomtype = "wktpoly";
                break;
            case "g":
                $geomtype = "wktsurface";
                break;
            default:
                die("Invalid Geometry");
                break;
        }

        $con = ConnectToDB();
        $req = pg_query_params($qry, array($netobj, $geomtype)) or
            die('Query failed: ' . pg_last_error());
        $payload = pg_fetch_row($req);
        return $payload[0];
    }

    function GetAttributesJSON($netobj, $param) {
        $fields = _parseAttributes("f", $_GET);

        $con = ConnectToDB();
        $qry = "SELECT tim_dat_attributes($1::TEXT, " . pg_toTextArray($con, $fields) . "::TEXT[])";
        $req = pg_query_params($qry, array($netobj)) or
            die('Query failed: ' . pg_last_error());
        $payload = pg_fetch_row($req);
        return $payload[0];
    }

    function GetTemporalAttributesJSON($netobj, $param) {
        $fields = _parseAttributes("f", $_GET);

        $con = ConnectToDB();
        $qry = "SELECT tim_dat_temporalattributes($1::TEXT, " . pg_toTextArray($con, $fields) . "::TEXT[])";
        $req = pg_query_params($qry, array($netobj)) or
            die('Query failed: ' . pg_last_error());
        $payload = pg_fetch_row($req);
        return $payload[0];
    }

?>