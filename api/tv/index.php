<?php
    include('_credentials.php');

    function ConnectToDB() {
        global $PGSQL_CONNECTION_STRING;
        $con = pg_connect($PGSQL_CONNECTION_STRING) or kill("Unabled to contact DB");
        return $con;
    }
    function kill($msg) {
        header('Content-Type: application/json');
        header('Content-Encoding: x-gzip');
        $dyingwords = gzencode(json_encode(array('error' => $msg)));
        header('Content-Length: ' . strlen($dyingwords));
        echo $dyingwords;
        die();
    }
    function _parseAttribute($att, $array, $ignoreerror = FALSE, $defval = -1) {
        if (array_key_exists($att, $array)) {
            return urldecode($array[$att]);
        } else {
            if ($ignoreerror) {
                return $defval;
            } else {
                kill('Missing parameter');
            }
        }
    }
    function shape($time) {
        $con = ConnectToDB();
        $qry = "SELECT * FROM trainview_gtfs_shapes($1)";
        $req = pg_query_params($qry, array($time)) or kill('Query failed: ' . pg_last_error());
        $payload = pg_fetch_row($req);
        $retval = gzencode($payload[0]);
        header('Content-Length: ' . strlen($retval));
        echo $retval;
    }
    function trainview($time, $hour) {
        $con = ConnectToDB();
        $qry = "
            SELECT json_agg(row_to_json((SELECT v FROM (SELECT trainno, data) v)))
            FROM (SELECT trip_short_name trainno, 
            json_agg((SELECT r FROM (SELECT line, ARRAY[ST_X(geom), ST_Y(geom)] coord, stdtime, late) r)) AS data
            FROM trainview_link_match_shape($1, $2)
            GROUP BY trainno) _q;
        ";
        $req = pg_query_params($qry, array($time, $hour)) or kill('Query failed: ' . pg_last_error());
        $payload = pg_fetch_row($req);
        $retval = gzencode($payload[0]);
        header('Content-Length: ' . strlen($retval));
        echo $retval;
    }

    $time = _parseAttribute("d", $_GET);
    $hour = _parseAttribute("h", $_GET, TRUE);
    $type = _parseAttribute("t", $_GET);
    header('Content-Type: application/json');
    header('Content-Encoding: x-gzip');
    switch($type) {
        case 's':
        case 'shape':
            shape($time);
            break;
        case 'tv':
        case 'trainview':
            trainview($time, $hour);
            break;
        default:
            kill("Invalid Type");
            break;
    }
?>