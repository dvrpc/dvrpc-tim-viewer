<?php
    include('_functions.php');

    $type = ParseType($_GET);

    function FUCKINGFUCK($key, $array) {
        $key_cntflag = $key . 'n';
        switch(_parseAttribute($key_cntflag, $array)) {
            case -1:
                return "(SELECT array_agg(no) FROM net_zone)";
                break;
            case 0:
                die("blarg, i'm ded");
                break;
            default:
                return pg_toIntArray(_parseAttributes($key, $array));
                break;
        }
    }

    $con = ConnectToDB();

    $origzonenos = FUCKINGFUCK("oz", $_GET);
    $destzonenos = FUCKINGFUCK("dz", $_GET);
    $tods = pg_toTextArray($con, _parseAttributes("tod", $_GET));
    $matrixno = _parseAttribute("m", $_GET);

    switch ($type) {
        case "ddl":
            $qry = "SELECT tim_gfx_ddl($1, " . $origzonenos . ", ". $destzonenos . ", " . $tods . ")";
            break;
        case "vddl":
            $qry = "SELECT tim_gfx_vddl($1, " . $origzonenos . ", ". $destzonenos . ", " . $tods . ")";
            break;
        default:
            die("Invalid type");
            break;
    }

    $req = pg_query_params($qry, array($matrixno)) or
        die('Query failed: ' . pg_last_error());
    $payload = pg_fetch_row($req);
    echo $payload[0];
?>