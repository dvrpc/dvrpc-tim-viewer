<?php
    include('_functions.php');
    header('Content-Encoding: x-gzip');
    $payload = gzencode(GetData("screenlines", $_GET));
    header('Content-Length: ' . strlen($payload));
    echo $payload;
?>