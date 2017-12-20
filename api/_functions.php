<?php
    include('credentials.php');

    function ConnectToDB() {
        global $PGSQL_CONNECTION_STRING;
        $con = pg_connect($PGSQL_CONNECTION_STRING) or
            die('Unable to connect: ' . pg_last_error());
        return $con;
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
?>