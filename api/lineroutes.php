<?php
    include('_functions.php');
    header('Content-Encoding: gzip');
    $payload = gzencode(GetGeoJSON("lineroutes", $_GET));
    header('Content-Length: ' . strlen($payload));
    echo $payload;
?>