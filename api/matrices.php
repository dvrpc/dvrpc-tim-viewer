<?php
    include("_functions.php");
    error_reporting(0);
    $matrixno = (int) _parseAttribute("m", $_GET);
    $zones = pg_toIntArray(_parseAttributes("z", $_GET));
    $con = ConnectToDB();
    $req = pg_query_params("SELECT tim_mtxvals_json($1," . $zones . ")", array($matrixno)) or
        die('[]');
    header('Content-Encoding: x-gzip');
    $payload = pg_fetch_row($req);
    header('Content-Length: ' . strlen($payload[0]));
    echo gzencode($payload[0]);
?>