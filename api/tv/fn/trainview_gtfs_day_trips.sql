-- Dependencies:
--  function/trainview_gtfs_day_ids
--  table/gtfs_trips
--  table/gtfs_stop_times

DROP FUNCTION IF EXISTS trainview_gtfs_day_trips(TEXT);
CREATE OR REPLACE FUNCTION trainview_gtfs_day_trips(isotime TEXT)
RETURNS TABLE (
    gtfs_id SMALLINT,
    service_id TEXT,
    route_id TEXT,
    trip_id TEXT,
    trip_headsign TEXT,
    trip_short_name TEXT,
    direction_id SMALLINT,
    shape_id TEXT,
    start_time INTERVAL,
    end_time INTERVAL
) AS $$
BEGIN
    RETURN QUERY
    with _gtfs_service_id AS (
        SELECT * FROM trainview_gtfs_day_ids(isotime)
    ),
    _trips AS (
        SELECT _trips.*
        FROM _gtfs_service_id
        LEFT JOIN gtfs_trips _trips
        ON _trips.gtfs_id = _gtfs_service_id.gtfs_id
        AND _trips.service_id = _gtfs_service_id.service_id
    ),
    _stop_times AS (
        SELECT
            _stop_times.gtfs_id,
            _stop_times.trip_id,
            min(arrival_time) start_time,
            max(departure_time) end_time 
        FROM _gtfs_service_id
        LEFT JOIN gtfs_stop_times _stop_times
        ON _gtfs_service_id.gtfs_id = _stop_times.gtfs_id
        GROUP BY _stop_times.gtfs_id, _stop_times.trip_id
    )
    SELECT
        _trips.gtfs_id,
        _trips.service_id,
        _trips.route_id,
        _trips.trip_id,
        _trips.trip_headsign,
        _trips.trip_short_name,
        _trips.direction_id,
        _trips.shape_id,
        _stop_times.start_time,
        _stop_times.end_time
    FROM _trips
    LEFT JOIN _stop_times
    ON _trips.gtfs_id = _stop_times.gtfs_id
    AND _trips.trip_id = _stop_times.trip_id;
END;
$$ LANGUAGE plpgsql;