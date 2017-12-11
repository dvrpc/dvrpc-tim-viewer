<?php
    include 'credentials.php';

    $_qry = "SELECT COUNT(*) FROM mtx_210_am WHERE oindex = $1;";
    if (ISSET($_GET['z'])) {
        $zoneno = $_GET['z'];
    } else {
        die('{}');
    }

    $con = pg_connect($PGSQL_CONNECTION_STRING) or
        die('Unable to connect: ' . pg_last_error());
    $req = pg_query_params($_qry, array($zoneno)) or
        die('Query failed: ' . pg_last_error());
    $payload = pg_fetch_array($req);

    echo json_encode($payload);
?>