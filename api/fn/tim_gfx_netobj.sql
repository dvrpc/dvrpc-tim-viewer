CREATE OR REPLACE FUNCTION tim_gfx_netobj(netobj TEXT, geomtype TEXT)
RETURNS JSON AS $$
DECLARE
    fields TEXT;
    geojson JSON;
BEGIN
    fields := tim_netobjids(netobj);
    EXECUTE(FORMAT('
    SELECT row_to_json(featurecollection)
    FROM (
        SELECT
            ''FeatureCollection'' AS type,
            array_to_json(array_agg(features)) AS features
        FROM (
            SELECT
                row_to_json((SELECT p FROM (SELECT %s) p)) AS properties,
                ''Feature'' AS type,
                ST_AsGeoJSON(%I, maxdecimaldigits:=5)::json AS geometry
            FROM geom_%I
        ) features
    ) featurecollection;
    ', fields, geomtype, netobj)) INTO geojson;
    RETURN geojson;
END;
$$ LANGUAGE plpgsql;