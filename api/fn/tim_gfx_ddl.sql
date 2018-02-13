CREATE OR REPLACE FUNCTION tim_gfx_ddl(matrixno INTEGER, origzoneno INTEGER, destzonenos INTEGER[], tods TEXT[])
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
            FROM tim_ddesire_table($1, $2, $3, $4)
        ) features
    ) featurecollection;
    ') USING matrixno, origzoneno, destzonenos, tods INTO geojson;
    RETURN geojson;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION tim_gfx_ddl(matrixno INTEGER, origzonenos INTEGER[], destzonenos INTEGER[], tods TEXT[])
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
            FROM tim_ddesire_table($1, $2, $3, $4)
        ) features
    ) featurecollection;
    ') USING matrixno, origzonenos, destzonenos, tods INTO geojson;
    RETURN geojson;
END;
$$ LANGUAGE plpgsql;