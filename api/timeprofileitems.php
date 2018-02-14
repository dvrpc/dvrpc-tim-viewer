<?php
    include('_functions.php');
    header('Content-Encoding: x-gzip');
    $payload = gzencode(GetData("timeprofileitem", $_GET));
    header('Content-Length: ' . strlen($payload));
    echo $payload;
?>
