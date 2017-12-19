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
    geom GEOMETRY
)  AS $$
DECLARE
    origzoneindex INTEGER;
    destzoneindices INTEGER[];
    dzno INTEGER;
    _tblname_mtx_am TEXT;
    _tblname_mtx_md TEXT;
    _tblname_mtx_pm TEXT;
    _tblname_mtx_nt TEXT;
BEGIN
    _tblname_mtx_am := format('%I', 'mtx_' || mtxno || '_am');
    _tblname_mtx_md := format('%I', 'mtx_' || mtxno || '_md');
    _tblname_mtx_pm := format('%I', 'mtx_' || mtxno || '_pm');
    _tblname_mtx_nt := format('%I', 'mtx_' || mtxno || '_nt');

    DROP TABLE IF EXISTS _destzone;
    DROP TABLE IF EXISTS _mtx_am;
    CREATE TEMPORARY TABLE _destzone (
        zoneindex INTEGER,
        zoneno INTEGER
    );
    CREATE TEMPORARY TABLE _test (
        oindex INTEGER, dindex INTEGER, val DOUBLE PRECISION
    );
    SELECT tim_getzoneindex(origzoneno) INTO origzoneindex;
    FOREACH dzno IN ARRAY destzonenos LOOP
        INSERT INTO _destzone VALUES (tim_getzoneindex(dzno), dzno);
    END LOOP;
    SELECT array_agg(_destzone.zoneindex) INTO destzoneindices FROM _destzone;

    EXECUTE FORMAT('INSERT INTO _test SELECT * FROM %I WHERE oindex = $1 AND dindex IN (SELECT DISTINCT(zoneindex) FROM _destzone);', _mtx_am) USING origzoneindex;

    RETURN QUERY WITH
    _mtx1 AS (
        SELECT mtx.*, dz.zoneno AS dno
        FROM _test mtx
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
            'SELECT id, ozone source, dzone target, length AS cost, length as reverse_cost FROM _debug_delaunay',
            origzoneindex,
            destzoneindices,
            directed := false
        ) fn
        LEFT JOIN _mtx1 ON _mtx1.dno = fn.end_vid
        GROUP BY fn.edge
    ) _q
    LEFT JOIN _debug_delaunay d
    ON d.id = _q.edge
    WHERE _q.totalval IS NOT NULL;
END;
$$ LANGUAGE plpgsql;