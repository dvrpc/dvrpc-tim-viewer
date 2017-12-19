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
    origzoneindex INTEGER;
    destzoneindices INTEGER[];
    _tblname_mtx_am TEXT;
    _tblname_mtx_md TEXT;
    _tblname_mtx_pm TEXT;
    _tblname_mtx_nt TEXT;
    dzno INTEGER;
BEGIN
    _tblname_mtx_am := format('%I', 'mtx_' || mtxno || '_am');
    _tblname_mtx_md := format('%I', 'mtx_' || mtxno || '_md');
    _tblname_mtx_pm := format('%I', 'mtx_' || mtxno || '_pm');
    _tblname_mtx_nt := format('%I', 'mtx_' || mtxno || '_nt');

    DROP TABLE IF EXISTS _destzone;
    DROP TABLE IF EXISTS _mtx_am;
    DROP TABLE IF EXISTS _mtx_md;
    DROP TABLE IF EXISTS _mtx_pm;
    DROP TABLE IF EXISTS _mtx_nt;

    CREATE TEMPORARY TABLE _destzone (
        zoneindex INTEGER,
        zoneno INTEGER
    );
    CREATE TEMPORARY TABLE _mtx_am (
        oindex INTEGER, dindex INTEGER, val DOUBLE PRECISION
    );

    SELECT tim_getzoneindex(origzoneno) INTO origzoneindex;
    FOREACH dzno IN ARRAY destzonenos LOOP
        INSERT INTO _destzone VALUES (tim_getzoneindex(dzno), dzno);
    END LOOP;
    SELECT array_agg(_destzone.zoneindex) INTO destzoneindices FROM _destzone;

    EXECUTE FORMAT('
        INSERT INTO _mtx_am
        SELECT *
        FROM %I
        WHERE oindex = $1
        AND dindex IN (SELECT DISTINCT(zoneindex) FROM _destzone);
        ', _tblname_mtx_am) USING origzoneindex;

    RETURN QUERY WITH
    _mtx AS (
        SELECT mtx.*, dz.zoneno AS dno
        FROM _mtx_am mtx
        LEFT JOIN _destzone dz ON dz.zoneindex = dindex
    )
    SELECT
        _q.edge,
        _q.totalval,
        d.ozone,
        d.dzone,
        d.geom::GEOMETRY(LINESTRING, 4326)
    FROM (
        SELECT fn.edge, SUM(val) totalval
        FROM pgr_dijkstra(
            'SELECT id, ozone source, dzone target, length AS cost, length as reverse_cost FROM _debug_delaunay',
            origzoneno,
            destzonenos,
            directed := false
        ) fn
        LEFT JOIN _mtx ON _mtx.dno = fn.end_vid
        GROUP BY fn.edge
    ) _q
    LEFT JOIN _debug_delaunay d
    ON d.id = _q.edge
    WHERE d.geom IS NOT NULL;
END;
$$ LANGUAGE plpgsql;