<?php
    include('_functions.php');

    $type = ParseType($_GET);

    $origzoneno = _parseAttribute("oz", $_GET);
    $destzonenos = _parseAttributes("dz", $_GET);
    $matrixno = _parseAttribute("m", $_GET);

    switch ($type) {
        case "ddl":
            $qry = "SELECT tim_gfx_ddl($1, $2,  ". pg_toIntArray($destzonenos) .")";
            break;
        case "vddl":
            $qry = "SELECT tim_gfx_vddl($1, $2, ". pg_toIntArray($destzonenos) .")";
            break;
        default:
            die("Invalid type");
    }

    $con = ConnectToDB();
    $req = pg_query_params($qry, array($matrixno, $origzoneno)) or
        die('Query failed: ' . pg_last_error());
    $payload = pg_fetch_row($req);
    echo $payload[0];
?>