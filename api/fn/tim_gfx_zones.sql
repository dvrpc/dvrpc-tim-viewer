CREATE OR REPLACE FUNCTION tim_gfx_zones(geomtype TEXT)
RETURNS JSON AS $$
DECLARE
    geojson JSON;
BEGIN
    EXECUTE(FORMAT('
    SELECT row_to_json(featurecollection)
    FROM (
        SELECT
            ''FeatureCollection'' AS type,
            array_to_json(array_agg(features)) AS features
        FROM (
            SELECT
                row_to_json((SELECT p FROM (SELECT no) p)) AS properties,
                ''Feature'' AS type,
                ST_AsGeoJSON(%I, maxdecimaldigits:=5)::json AS geometry
            FROM geom_zones
        ) features
    ) featurecollection;
    ', geomtype)) INTO geojson;
    RETURN geojson;
END;
$$ LANGUAGE plpgsql;