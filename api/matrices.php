<?php
    include("_functions.php");
    $matrixno = (int) _parseAttribute("m", $_GET);
    $zones = pg_toIntArray(_parseAttributes("z", $_GET));
    $con = ConnectToDB();
    $req = pg_query_params("SELECT tim_mtxvals_json($1," . $zones . ")", array($matrixno)) or
        die('Query failed: ' . pg_last_error());
    $payload = pg_fetch_row($req);
    echo $payload[0];
?>