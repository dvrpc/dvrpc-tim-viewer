CREATE OR REPLACE FUNCTION tim_ddesire_table (
    mtxno INTEGER,
    origzoneno INTEGER,
    destzonenos INTEGER[],
    tods TEXT[]
)
RETURNS TABLE (
    edge BIGINT,
    totalval REAL,
    ozone INTEGER,
    dzone INTEGER,
    geom GEOMETRY(LINESTRING, 4326)
)  AS $$
DECLARE
    _mtx_tbl TEXT;
BEGIN
    _mtx_tbl := FORMAT('%I', 'mtx_' || mtxno);
    RETURN QUERY
    EXECUTE FORMAT('
    WITH _mtx AS (
        SELECT * FROM %I
        WHERE ozoneno = $1
        AND tod = ANY($3)
    )
    SELECT
        _q.edge,
        _q.totalval,
        d.ozone,
        d.dzone,
        d.geom
    FROM (
        SELECT fn.edge, SUM(val) totalval
        FROM pgr_dijkstra(
            ''
            SELECT
                id,
                ozone source,
                dzone target,
                length AS cost,
                length as reverse_cost
            FROM gfx_zone_delaunay
            '',
            $1,
            $2,
            directed := false
        ) fn
        LEFT JOIN _mtx ON _mtx.dzoneno = fn.end_vid
        GROUP BY fn.edge
    ) _q
    LEFT JOIN gfx_zone_delaunay d
    ON d.id = _q.edge
    WHERE d.geom IS NOT NULL;
    ', _mtx_tbl) USING origzoneno, destzonenos, tods;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION tim_ddesire_table(
    matrixno INTEGER,
    origzonenos INTEGER[],
    destzonenos INTEGER[],
    tods TEXT[]
)
RETURNS TABLE (
    edge BIGINT,
    totalval REAL,
    geom GEOMETRY(LINESTRING, 4326)
) AS $$
DECLARE
    geojson JSON;
BEGIN
    RETURN QUERY
    SELECT (_q.rec).edge, SUM((_q.rec).totalval) totalval, (_q.rec).geom
    FROM (
        SELECT tim_ddesire_table(matrixno, origzoneno, destzonenos, tods) rec
        FROM (SELECT UNNEST(origzonenos) origzoneno) _q
    ) _q
    GROUP BY (_q.rec).edge, (_q.rec).geom;
END;
$$ LANGUAGE plpgsql;