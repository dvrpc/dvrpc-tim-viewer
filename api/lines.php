<?php
    include('_functions.php');
    header('Content-Encoding: x-gzip');
    $payload = gzencode(GetData("line", $_GET));
    header('Content-length: ' . strlen($payload));
    echo $payload;
?>
