-- Dependencies:
--  function/trainview_gtfs_day_ids
--  table/gtfs_shapes

CREATE OR REPLACE FUNCTION trainview_gtfs_shapes(isotime TEXT)
RETURNS JSON AS $$
DECLARE
    retval JSON;
BEGIN
    WITH _shapes AS (
        SELECT
            _shapes.shape_id,
            ST_MakeLine(array_agg(ST_SetSRID(ST_MakePoint(shape_pt_lon, shape_pt_lat), 4326))) geom
        FROM (
            SELECT DISTINCT(gtfs_id) FROM trainview_gtfs_day_ids(isotime)
        ) _gtfs_ids
        LEFT JOIN gtfs_shapes _shapes
        ON _gtfs_ids.gtfs_id = _shapes.gtfs_id
        GROUP BY _shapes.shape_id
    )
    SELECT row_to_json(fc) INTO retval
    FROM (
        SELECT
            'FeatureCollection' AS type,
            json_agg(row_to_json(f)) AS features
        FROM (
            SELECT
                'Feature' AS type,
                (SELECT p FROM (SELECT shape_id id) p) properties,
                ST_AsGeoJSON(geom)::json geometry
            FROM _shapes
        ) f
    ) fc;
    RETURN retval;
END;
$$ LANGUAGE plpgsql;