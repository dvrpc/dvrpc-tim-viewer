<?php
    include('_functions.php');
    $qry = "SELECT tim_getschema();";
    $con = ConnectToDB();
    $req = pg_query_params($qry, array()) or
        die('Query failed: ' . pg_last_error());
    $payload = pg_fetch_row($req);
    echo $payload[0];
?>