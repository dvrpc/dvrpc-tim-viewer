<?php
    // Default is 128M
    ini_set('memory_limit','256M');
    include('_functions.php');
    $type = ParseType($_GET);
    $fields = _parseAttributes("f", $_GET);
    $netobj = "links";

    $con = ConnectToDB();
    $qry = "SELECT tim_dat_temporalattributes($1::TEXT, " . pg_toTextArray($con, $fields) . "::TEXT[])";
    $req = pg_query_params($qry, array($netobj)) or
        die('Query failed: ' . pg_last_error());
    $payload = pg_fetch_row($req);
    header("Content-Encoding: gzip");
    echo gzencode($payload[0]);
?>