<?php
    include('_functions.php');

    var_dump(ParseAttributes($_GET));

    $_qry = "SELECT COUNT(*) FROM mtx_2000_am WHERE oindex = $1;";
    $con = ConnectToDB();
    $req = pg_query_params($_qry, array(135)) or
        die('Query failed: ' . pg_last_error());
    $payload = pg_fetch_array($req);
    echo json_encode($payload);
?>