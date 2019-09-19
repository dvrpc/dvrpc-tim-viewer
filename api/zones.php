<?php
    include('_functions.php');
    header('Content-Type: application/json');
    header('Content-Encoding: x-gzip');
    $response = Operator(
        "zones",
        $_SERVER['REQUEST_METHOD'],
        $_GET,
        trim(file_get_contents("php://input"))
    );
    $payload = gzencode($response);
    header('Content-Length: ' . strlen($payload));
    echo $payload;
?>