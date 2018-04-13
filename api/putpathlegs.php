<?php
    include('_functions.php');

    $qry = "
        WITH cws AS (
        SELECT -- *,
            ozoneno,
            dzoneno,
            pathindex,
            pathlegindex,
            odtrips,
            ARRAY[fromstoppointno, tostoppointno] odstoppointnos,
            CASE WHEN linename IS NULL THEN 
                ARRAY[timeprofilekeystring, NULL]
            ELSE 
                ARRAY[linename, tsyscode]
            END descrip
        FROM putpathlegs
        WHERE
            (fromstoppointno IS NOT NULL AND tostoppointno IS NOT NULL)
        AND ozoneno = $1
        AND TOD = $2
        AND scen = '2015'

        ORDER BY ozoneno, dzoneno, pathindex, pathlegindex
        ),
        acws AS (
        SELECT
            ozoneno, dzoneno, pathindex,
            AVG(odtrips) odtrips,
            array_agg(odstoppointnos) odstoppointnos,
            array_agg(descrip) descripts
        FROM cws
        GROUP BY ozoneno, dzoneno, pathindex
        )
        SELECT json_agg(row_to_json(acws))
        FROM acws;
    ";

    $con = ConnectToDB();

    $origzoneno = _parseAttribute("o", $_GET);
    $tod = _parseAttribute("tod", $_GET);

    $req = pg_query_params($qry, array($origzoneno, $tod)) or
        die('Query failed: ' . pg_last_error());
    $payload = pg_fetch_row($req);
    echo $payload[0];
?>