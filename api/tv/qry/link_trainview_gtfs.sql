WITH gtfst AS (
SELECT
    trip_short_name, 
    array_agg(route_id) route_ids,
    array_agg(trip_id) trip_ids, 
    array_agg(shape_id) shape_ids,
    min(start_time) start_time, 
    max(end_time) end_time
FROM (SELECT * FROM trainview_gtfs_day_trips('2018-02-05 00:00:00') ORDER BY start_time) gtfst
GROUP BY trip_short_name
),
_ultra AS (
SELECT *,
    -- tvd.*,
    ('2018-02-05 00:00:00'::timestamp + gtfst.start_time) astart_time,
    ('2018-02-05 00:00:00'::timestamp + gtfst.end_time) aend_time
FROM trainview_day_data('2018-02-05 00:00:00') tvd
INNER JOIN gtfst
ON tvd.trainno = gtfst.trip_short_name
),

-- Slowest?
--  WITH _shapes AS (
--  	SELECT _shapes.*
--  	FROM (SELECT DISTINCT(gtfs_id) FROM trainview_gtfs_day_ids('2018-02-14')) _gtfs_id
--  	LEFT JOIN gtfs_shapes _shapes
--  	ON _shapes.gtfs_id = _gtfs_id.gtfs_id
--  	ORDER BY shape_id, shape_pt_sequence
--  )
--  SELECT _shapes.shape_id,
--  ST_MakeLine(array_agg(ST_SetSRID(ST_MakePoint(shape_pt_lon, shape_pt_lat), 4326)))
--  FROM (SELECT DISTINCT(shape_id) FROM trainview_gtfs_day_trips('2018-02-14')) _trips
--  LEFT JOIN _shapes
--  ON _shapes.shape_id = _trips.shape_id
--  GROUP BY _shapes.shape_id
--

-- Slower?
--  WITH _shape_ids AS (
--  SELECT gtfs_id, shape_id FROM trainview_gtfs_day_trips('2018-02-14')
--  GROUP BY gtfs_id, shape_id
--  ),
--  _shapes AS (
--  SELECT _shapes.*
--  FROM _shape_ids LEFT JOIN gtfs_shapes _shapes
--  ON _shapes.gtfs_id = _shape_ids.gtfs_id
--  AND _shapes.shape_id = _shape_ids.shape_id
--  ORDER BY shape_id, shape_pt_sequence
--  )
--  SELECT shape_id,
--  ST_MakeLine(array_agg(ST_SetSRID(ST_MakePoint(shape_pt_lon, shape_pt_lat), 4326)))
--  FROM _shapes
--  GROUP BY shape_id
--

-- Def fastest tho
_shapes AS (
    SELECT _shapes.shape_id,
    ST_MakeLine(array_agg(ST_SetSRID(ST_MakePoint(shape_pt_lon, shape_pt_lat), 4326))) geom
    FROM (SELECT DISTINCT(gtfs_id) FROM trainview_gtfs_day_ids('2018-02-05 00:00:00')) _gtfs_ids
    LEFT JOIN gtfs_shapes _shapes
    ON _gtfs_ids.gtfs_id = _shapes.gtfs_id
    GROUP BY _shapes.shape_id
),
_full_lines AS (
    SELECT shape_ids, ST_LineMerge(ST_Collect(geom)) geom
    FROM (SELECT DISTINCT(shape_ids) FROM _ultra) _u
    LEFT JOIN _shapes
    ON _shapes.shape_id = ANY(shape_ids)
    GROUP BY shape_ids
)
SELECT
    -- ARRAY[lat, lon]::REAL[]
    _ultra.tstz,
    line,
    late,
    ST_ShortestLine(ST_SetSRID(ST_MakePoint(lon, lat), 4326), _full_lines.geom),
    _ultra.shape_ids
FROM _ultra
LEFT JOIN _full_lines
ON _full_lines.shape_ids = _ultra.shape_ids
WHERE
    tstz > (astart_time - '1 hour'::interval)
AND tstz < (aend_time + '4 hours'::interval)
AND EXTRACT(HOUR FROM astart_time) = 20
ORDER BY astart_time, tstz