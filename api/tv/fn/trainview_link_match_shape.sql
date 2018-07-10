-- Dependencies:
--  function/trainview_gtfs_day_trips
--  function/trainview_day_data
--  function/trainview_gtfs_day_ids
--  table/gtfs_shapes

DROP FUNCTION IF EXISTS trainview_link_match_shape(TEXT, INTEGER);
CREATE OR REPLACE FUNCTION trainview_link_match_shape(isotime TEXT, dep_hour INTEGER)
RETURNS TABLE (
    stdtime INTERVAL,
    trip_short_name TEXT,
    line TEXT,
    late INTEGER,
    geom GEOMETRY
) AS $$
DECLARE
    all_hours BOOLEAN;
BEGIN

    IF dep_hour < 0 THEN
        all_hours := TRUE;
    ELSE
        all_hours := FALSE;
    END IF;

    RETURN QUERY
    WITH gtfst AS (
    SELECT
        gtfst.trip_short_name, 
        array_agg(route_id) route_ids,
        array_agg(trip_id) trip_ids, 
        array_agg(shape_id) shape_ids,
        min(start_time) start_time, 
        max(end_time) end_time
    FROM (SELECT * FROM trainview_gtfs_day_trips(isotime) ORDER BY start_time) gtfst
    GROUP BY gtfst.trip_short_name
    ),
    _ultra AS (
        SELECT *,
            (isotime::timestamp + gtfst.start_time) astart_time,
            (isotime::timestamp + gtfst.end_time) aend_time
        FROM trainview_day_data(isotime) tvd
        INNER JOIN gtfst
        ON tvd.trainno = gtfst.trip_short_name
    ),
    _shapes AS (
        SELECT _shapes.shape_id,
        ST_MakeLine(array_agg(ST_SetSRID(ST_MakePoint(shape_pt_lon, shape_pt_lat), 4326))) geom
        FROM (SELECT DISTINCT(gtfs_id) FROM trainview_gtfs_day_ids(isotime)) _gtfs_ids
        LEFT JOIN gtfs_shapes _shapes
        ON _gtfs_ids.gtfs_id = _shapes.gtfs_id
        GROUP BY _shapes.shape_id
    ),
    _full_lines AS (
        SELECT shape_ids, ST_LineMerge(ST_Collect(_shapes.geom)) geom
        FROM (SELECT DISTINCT(shape_ids) FROM _ultra) _u
        LEFT JOIN _shapes
        ON _shapes.shape_id = ANY(shape_ids)
        GROUP BY shape_ids
    )
    SELECT
        (tstz - isotime::TIMESTAMP) stdtime,
        _ultra.trip_short_name,
        _ultra.line,
        _ultra.late,
        ST_EndPoint(ST_ShortestLine(ST_SetSRID(ST_MakePoint(lon, lat), 4326), _full_lines.geom)) geom
    FROM _ultra
    LEFT JOIN _full_lines
    ON _full_lines.shape_ids = _ultra.shape_ids
    WHERE
        tstz > (astart_time - '1 hour'::interval)
    AND tstz < (aend_time + '4 hours'::interval)
    AND (all_hours OR (EXTRACT(HOUR FROM astart_time) = dep_hour))
    ORDER BY astart_time, tstz;

END;
$$ LANGUAGE plpgsql;