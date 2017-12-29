<?php

    if (strcasecmp($_SERVER['REQUEST_METHOD'], 'POST') <> 0) {
        die('Request method must be POST');
    }
    $payload = trim(file_get_contents("php://input"));
    try {
        $decoded = json_decode($payload, true);
    } catch (Exception $e) {
        die('Unable to decode JSON');
    }

    if (!is_array($decoded)) {
        die('Invalid JSON');
    }
    var_dump($decoded);

?>
