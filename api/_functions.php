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
        return $pgarray . $array[$n - 1] . "]";
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
        /* Types
         *  b - Bureaucracy (Identifiers)
         *  d - Data
         *  g - Geometries
         *      gpt - Point
         *      gln - Line
         *      gpg - Polygon
         */
        if (array_key_exists("t", $get)) {
            return $get["t"];
        } else {
            die('Missing type parameter');
        }
    }

    function GetGeoJSON($netobj, $param) {
        $qry = "SELECT tim_gfx_netobj($1,$2)";
        switch (ParseType($param)) {
            case "gpt":
                $geomtype = "wktloc";
                break;
            case "gln":
                $geomtype = "wktpoly";
                break;
            case "gpg":
                $geomtype = "wktsurface";
                break;
            default:
                die("Invalid type");
        }

        $con = ConnectToDB();
        $req = pg_query_params($qry, array($netobj, $geomtype)) or
            die('Query failed: ' . pg_last_error());
        $payload = pg_fetch_row($req);
        return $payload[0];
    }
?>