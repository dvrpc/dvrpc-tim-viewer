<?php
    include('_functions.php');

    $type = ParseType($_GET);
    $atts = ParseAttributes($_GET);

    // OH BOY OH BOY OH BOY THERE YOU ARE MR. switch
    switch ($type) {
        case "gpt":
            $qry = "SELECT tim_gfx_zones('wktloc')";
            break;
        case "gln":
            $qry = "SELECT tim_gfx_zones('wktpoly')";
            break;
        case "gpg":
            $qry = "SELECT tim_gfx_zones('wktsurface')";
            break;
        default:
            die("Invalid type");
    }

    $con = ConnectToDB();
    $req = pg_query_params($qry, array()) or
        die('Query failed: ' . pg_last_error());
    $payload = pg_fetch_row($req);
    echo $payload[0];
?>