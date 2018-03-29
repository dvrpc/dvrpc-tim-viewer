CREATE OR REPLACE FUNCTION tim_put_timetable(lname TEXT)
RETURNS JSON AS $$
DECLARE
    geojson JSON;
BEGIN

    WITH
    vj AS (
        SELECT
            timeprofilename,
            dep
        FROM net_vehjourney
        WHERE linename = lname
    ),
    tpi AS (
        SELECT
            tpi.linename,
            tpi.lineroutename,
            tpi.directioncode,
            tpi.arr,
            tpi.timeprofilename,
            tpi.lritemindex,
            vj.dep startdep
        FROM vj
        LEFT JOIN net_timeprofileitem tpi
        ON vj.timeprofilename = tpi.timeprofilename
        WHERE alight = 1
        OR board = 1
    ),
    tt AS (
    SELECT
        lri.lineroutename,
        tpi.startdep::timestamp + tpi.arr::time stoptime,
        tpi.directioncode,
        lri.stoppointno
    FROM tpi
    LEFT JOIN net_linerouteitem lri
    ON tpi.linename = lri.linename
    AND tpi.lineroutename = lri.lineroutename
    AND tpi.directioncode = lri.directioncode
    AND tpi.lritemindex = lri.index
    ORDER BY tpi.timeprofilename, tpi.lritemindex
    )
    SELECT
        json_agg(row_to_json(
            (SELECT r FROM (SELECT lineroutename, stoptimes) r)
        )) INTO geojson
    FROM (
        SELECT
            lineroutename,
            json_agg(row_to_json((SELECT r FROM (SELECT
                stoptime,
                directioncode,
                stoppointno
            ) r))) stoptimes
        FROM tt
        GROUP BY lineroutename
    ) q;
    RETURN geojson;
END;
$$ LANGUAGE plpgsql;