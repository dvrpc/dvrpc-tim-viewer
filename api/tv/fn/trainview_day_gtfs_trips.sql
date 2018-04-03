CREATE OR REPLACE FUNCTION trainview_day_trips (isodate TEXT)
RETURNS TABLE (
    route_id 
    trip_id
    trip_short_name TEXT,
    trip_headsign TEXT,
    direction_id SMALLINT,
    shape_id TEXT
) AS $$
DECLARE
    isotimestamp TIMESTAMP;
BEGIN

    WITH cal AS (
    SELECT
    gtfs_id,
    service_id,
    start_date,
    end_date,
    (row_to_json((SELECT d FROM (SELECT monday, tuesday, wednesday, thursday, friday, saturday, sunday) d)) ->> trim(both ' ' FROM TO_CHAR('2017-11-04 00:00'::timestamp, 'day')))::smallint valid_service_id
    FROM gtfs_calendar
    WHERE
        start_date <= '2017-11-04 00:00'::timestamp
    AND end_date >= '2017-11-04 00:00'::timestamp  + '1 day'::interval
    ),
    sel_gtfs_service_id AS (
    SELECT * FROM cal WHERE valid_service_id = 1
    ORDER BY gtfs_id DESC
    LIMIT 1
    )
    SELECT -- _trips.* 
        route_id,
        trip_id,
        trip_short_name,
        trip_headsign,
        direction_id,
        shape_id
    FROM gtfs_trips _trips
    INNER JOIN sel_gtfs_service_id _sel
    ON _sel.gtfs_id = _trips.gtfs_id
    AND _sel.service_id = _trips.service_id

    ORDER BY route_id, trip_short_name

END;
$$ LANGUAGE plpgsql;