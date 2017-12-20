CREATE OR REPLACE FUNCTION tim_gfx_zones()
RETURNS JSON AS $$
DECLARE
    geojson JSON;
BEGIN

    SELECT row_to_json(featurecollection) INTO geojson
    FROM (
        SELECT
            'FeatureCollection' AS type,
            array_to_json(array_agg(features)) AS features
        FROM (
            SELECT
                row_to_json((SELECT p FROM (SELECT no) p)) AS properties,
                'Feature' AS type,
                ST_AsGeoJSON(wktloc)::json AS geometry
            FROM geom_zones
        ) features
    ) featurecollection;
    return geojson;

END;
$$ LANGUAGE plpgsql;