<?php
    include('_functions.php');
    header('Content-Encoding: x-gzip');
    $linename = _parseAttribute("ln", $_GET);
    $qry = "SELECT tim_put_timetable($1)";
    $con = ConnectToDB();
    $req = pg_query_params($qry, array($linename)) or kill("DB Error");
    $payload = pg_fetch_row($req);
    if ((!$payload > 0) || ($payload[0] == NULL)) {
        kill("No result");
    }
    $payload = gzencode($payload[0]);
    header('Content-Length: ' . strlen($payload));
    echo $payload;
?>