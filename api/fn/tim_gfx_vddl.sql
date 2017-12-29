CREATE OR REPLACE FUNCTION tim_gfx_vddl(matrixno INTEGER, origzoneno INTEGER, destzonenos INTEGER[])
RETURNS JSON AS $$
DECLARE
    geojson JSON;
BEGIN
    EXECUTE('
    SELECT row_to_json(featurecollection)
    FROM (
        SELECT
            ''FeatureCollection'' AS type,
            array_to_json(array_agg(features)) AS features
        FROM (
            SELECT
                row_to_json((SELECT p FROM (SELECT edge, totalval) p)) AS properties,
                ''Feature'' AS type,
                ST_AsGeoJSON(geom, maxdecimaldigits:=5)::json AS geometry
            FROM tim_vddesire_table($1, $2, $3)
        ) features
    ) featurecollection;
    ') USING matrixno, origzoneno, destzonenos INTO geojson;
    RETURN geojson;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION tim_gfx_vddl(matrixno INTEGER, origzonenos INTEGER[], destzonenos INTEGER[])
RETURNS JSON AS $$
DECLARE
    geojson JSON;
BEGIN
    EXECUTE('
    SELECT row_to_json(featurecollection)
    FROM (
        SELECT
            ''FeatureCollection'' AS type,
            array_to_json(array_agg(features)) AS features
        FROM (
            SELECT
                row_to_json((SELECT p FROM (SELECT edge, totalval) p)) AS properties,
                ''Feature'' AS type,
                ST_AsGeoJSON(geom, maxdecimaldigits:=5)::json AS geometry
            FROM tim_vddesire_table($1, $2, $3)
        ) features
    ) featurecollection;
    ') USING matrixno, origzonenos, destzonenos INTO geojson;
    RETURN geojson;
END;
$$ LANGUAGE plpgsql;