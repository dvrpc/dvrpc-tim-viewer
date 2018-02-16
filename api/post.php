<?php
    include('_functions.php');

    function kill($msg) {
        die(json_encode(array('error' => $msg)));
    }

    if (strcasecmp($_SERVER['REQUEST_METHOD'], 'GET') == 0) {
        kill('GET');
    } else if (strcasecmp($_SERVER['REQUEST_METHOD'], 'POST') == 0) {
        $post_payload = trim(file_get_contents("php://input"));
        try {
            $post = json_decode($post_payload, true);
        } catch (Exception $e) {
            kill("Invalid POST JSON");
        }
    } else {
        kill(":(");
    }

    $con = ConnectToDB();
    $netobj = NULL;

    $SQL_GET_KEYS = "SELECT field FROM tim_netobj_keys WHERE netobj = $1::TEXT";

    if (array_key_exists("netobj", $post)) {
        $netobj = $post["netobj"];
    } else {
        kill("Missing required key 'netobj'");
    }

    if (array_key_exists("keys", $post)) {
        
    } else {
        kill("Missing required key 'keys'");
    }

    $req = pg_query_params($SQL_GET_KEYS, array($netobj)) or kill('DB Error');
    $payload = pg_fetch_array($req);

    die(json_encode(array(
        'netobj' => $netobj,
        'dbkeys' => $payload
    )));

?>
