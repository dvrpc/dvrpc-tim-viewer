CREATE OR REPLACE FUNCTION tim_ddesire_table (
    mtxno INTEGER,
    origzoneno INTEGER,
    destzonenos INTEGER[]
)
RETURNS TABLE (
    edge BIGINT,
    totalval DOUBLE PRECISION,
    ozone INTEGER,
    dzone INTEGER,
    geom GEOMETRY(LINESTRING, 4326)
)  AS $$
DECLARE
    _tblname_mtx_am TEXT;
    _tblname_mtx_md TEXT;
    _tblname_mtx_pm TEXT;
    _tblname_mtx_nt TEXT;
    origzoneindex INTEGER;
BEGIN
    _tblname_mtx_am := format('%I', 'mtx_' || mtxno || '_am');
    _tblname_mtx_md := format('%I', 'mtx_' || mtxno || '_md');
    _tblname_mtx_pm := format('%I', 'mtx_' || mtxno || '_pm');
    _tblname_mtx_nt := format('%I', 'mtx_' || mtxno || '_nt');
    origzoneindex := tim_getzoneindex(origzoneno);

    RETURN QUERY
    EXECUTE FORMAT('
    WITH
    _destzone AS (
        SELECT indexp1 - 1 AS zoneindex, no zoneno
        FROM (
            SELECT row_number() OVER (ORDER BY no) AS indexp1, no FROM net_zones
        ) _q
        WHERE no IN (SELECT UNNEST($1))
    ),
    _mtx AS (
        SELECT mtx.*, dz.zoneno AS dno
        FROM (
            SELECT *
            FROM %I
            WHERE oindex = $2
            AND dindex IN (SELECT zoneindex FROM _destzone)
        ) mtx
        LEFT JOIN _destzone dz ON dz.zoneindex = dindex
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
            ''SELECT id, ozone source, dzone target, length AS cost, length as reverse_cost FROM gfx_zone_delaunay'',
            $3,
            (SELECT array_agg(zoneno) FROM _destzone),
            directed := false
        ) fn
        LEFT JOIN _mtx ON _mtx.dno = fn.end_vid
        GROUP BY fn.edge
    ) _q
    LEFT JOIN gfx_zone_delaunay d
    ON d.id = _q.edge
    WHERE d.geom IS NOT NULL;
    ', _tblname_mtx_am) USING destzonenos, origzoneindex, origzoneno;

END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION tim_ddesire_table(matrixno INTEGER, origzonenos INTEGER[], destzonenos INTEGER[])
RETURNS TABLE (
    edge BIGINT,
    totalval DOUBLE PRECISION,
    geom GEOMETRY(LINESTRING, 4326)
) AS $$
DECLARE
    geojson JSON;
BEGIN
    RETURN QUERY
    SELECT (_q.rec).edge, SUM((_q.rec).totalval) totalval, (_q.rec).geom
    FROM (
        SELECT tim_ddesire_table(matrixno, origzoneno, destzonenos) rec
        FROM (SELECT UNNEST(origzonenos) origzoneno) _q
    ) _q
    GROUP BY (_q.rec).edge, (_q.rec).geom;
END;
$$ LANGUAGE plpgsql;