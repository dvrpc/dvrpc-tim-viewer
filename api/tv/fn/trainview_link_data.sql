-- Dependencies:
--  function/trainview_gtfs_day_trips
--  function/trainview_day_data


CREATE OR REPLACE FUNCTION trainview_link_data(isotime TEXT)
RETURNS TABLE (
    timestmp TIMESTAMP,
    line TEXT,
    service TEXT,
    trainno TEXT,
    consist TEXT[],
    -- consistlength SMALLINT,
    origin TEXT,
    destination TEXT,
    nextstop TEXT,
    late SMALLINT,
    lat REAL,
    lon REAL
) AS $$
BEGIN
    RETURN QUERY
    with gtfst AS (
        SELECT
            trip_short_name,
            array_agg(route_id),
            min(start_time) start_time,
            max(end_time) end_time
        FROM trainview_gtfs_day_trips(isotime)
        GROUP BY trip_short_name
    ),
    _ultra AS (
        SELECT
            tvd.*,
            (isotime::timestamp + gtfst.start_time) astart_time,
            (isotime::timestamp + gtfst.end_time) aend_time,
        FROM trainview_day_data(isotime) tvd
        INNER JOIN gtfst
        ON tvd.trainno = gtfst.trip_short_name
    )
    SELECT
        _ultra.timestmp,
        _ultra.line,
        _ultra.service,
        _ultra.trainno,
        _ultra.consist,
        -- _ultra.consistlength,
        _ultra.origin,
        _ultra.destination,
        _ultra.nextstop,
        _ultra.late,
        _ultra.lat, _ultra.lon
    FROM _ultra
    WHERE
        timestmp > (astart_time - '1 hour'::interval)
    AND timestmp < (aend_time + '4 hours'::interval);
END;
$$ LANGUAGE plpgsql;
