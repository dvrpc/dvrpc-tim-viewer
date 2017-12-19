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
BEGIN
    _tblname_mtx_am := format('%I', 'mtx_' || mtxno || '_am');
    _tblname_mtx_md := format('%I', 'mtx_' || mtxno || '_md');
    _tblname_mtx_pm := format('%I', 'mtx_' || mtxno || '_pm');
    _tblname_mtx_nt := format('%I', 'mtx_' || mtxno || '_nt');

    RETURN QUERY
    EXECUTE FORMAT('
    WITH
    _destzone AS (
        SELECT
            tim_getzoneindex(no) zoneindex,
            no zoneno
        FROM net_zones
        WHERE no IN (SELECT UNNEST($1))
    ),
    _mtx AS (
        SELECT mtx.*, dz.zoneno AS dno
        FROM (
            SELECT *
            FROM %I
            WHERE oindex = tim_getzoneindex($2)
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
            ''SELECT id, ozone source, dzone target, length AS cost, length as reverse_cost FROM _debug_delaunay'',
            $3,
            (SELECT array_agg(zoneno) FROM _destzone),
            directed := false
        ) fn
        LEFT JOIN _mtx ON _mtx.dno = fn.end_vid
        GROUP BY fn.edge
    ) _q
    LEFT JOIN _debug_delaunay d
    ON d.id = _q.edge
    WHERE d.geom IS NOT NULL;
    ', _tblname_mtx_am) USING destzonenos, origzoneno, origzoneno;
END;
$$ LANGUAGE plpgsql;