CREATE OR REPLACE FUNCTION tim_gfx_netobj(netobj TEXT, geomtype TEXT)
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
            FROM geom_%I
        ) features
    ) featurecollection;
    ', geomtype, netobj)) INTO geojson;
    RETURN geojson;
END;
$$ LANGUAGE plpgsql;