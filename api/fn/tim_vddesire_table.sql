CREATE OR REPLACE FUNCTION tim_vddesire_table (
    mtxno INTEGER,
    origzoneno INTEGER,
    destzonenos INTEGER[]
)
RETURNS TABLE (
    edge BIGINT,
    totalval DOUBLE PRECISION,
    geom GEOMETRY(LINESTRING, 4326)
) AS $$
DECLARE
    _tblname_mtx_am TEXT;
    _tblname_mtx_md TEXT;
    _tblname_mtx_pm TEXT;
    _tblname_mtx_nt TEXT;
    origzoneindex INTEGER;
    origzoneid INTEGER;
BEGIN
    _tblname_mtx_am := format('%I', 'mtx_' || mtxno || '_am');
    _tblname_mtx_md := format('%I', 'mtx_' || mtxno || '_md');
    _tblname_mtx_pm := format('%I', 'mtx_' || mtxno || '_pm');
    _tblname_mtx_nt := format('%I', 'mtx_' || mtxno || '_nt');
    origzoneindex := tim_getzoneindex(origzoneno);
    SELECT id INTO origzoneid FROM _debug_network_zones WHERE no = origzoneno;

    RETURN QUERY
    WITH
    zone_index AS (
        SELECT indexp1 - 1 AS index, no
        FROM (
            SELECT row_number() OVER (ORDER BY no) AS indexp1, no
            FROM net_zones
        ) _q
    ),
    _destzone AS (
        SELECT indexp1 - 1 AS zoneindex, zoneno, nz.id zoneid
        FROM (
            SELECT
                row_number() OVER (ORDER BY no) AS indexp1,
                net_zones.no zoneno
            FROM net_zones
        ) _q
        LEFT JOIN _debug_network_zones nz ON nz.no = _q.zoneno
        WHERE zoneno IN (SELECT UNNEST(destzonenos))
    )
    SELECT sp.*, net.geom FROM (
        SELECT fn.edge, SUM(val) totalval
        FROM pgr_dijkstra(FORMAT('
            SELECT id, source, target, cost AS cost, rcost as reverse_cost
            FROM (
                SELECT id, source, target,
                    fwd * length AS cost,
                    rev * length AS rcost
                FROM (
                    SELECT
                        id, source, target,
                        ST_Length(geom) length,
                        (ozone IS NULL AND dzone IS NULL)::integer tflag,
                    CASE
                        WHEN ozone IS NULL AND dzone IS NULL THEN 1
                        WHEN ozone IS NULL THEN CASE
                            WHEN dzone = %s THEN 999999
                            ELSE 1
                        END
                        ELSE CASE
                            WHEN ozone = %s THEN 1
                            ELSE 999999
                        END
                    END fwd,
                    CASE
                        WHEN dzone IS NULL AND ozone IS NULL THEN 1
                        WHEN dzone IS NULL THEN CASE
                            WHEN ozone = %s THEN 999999
                            ELSE 1
                        END
                        ELSE CASE
                            WHEN dzone = %s THEN 1
                            ELSE 999999
                        END
                        END rev
                    FROM _debug_network
                ) __q
            ) _q', origzoneno, origzoneno, origzoneno, origzoneno),
            origzoneid,
            (SELECT array_agg(DISTINCT(zoneid)) FROM _destzone),
            directed := true
        ) fn
        LEFT JOIN _debug_network_zones z ON z.id = fn.end_vid
        LEFT JOIN zone_index zi ON z.no = zi.no
        -- LEFT JOIN _destzone dz ON dz.zoneno = z.no
        LEFT JOIN mtx_2000_am mtx ON mtx.oindex = origzoneindex AND mtx.dindex = zi.index
        -- LEFT JOIN mtx_2000_am mtx ON mtx.oindex = 134 AND mtx.dindex = dz.zoneindex
        GROUP BY fn.edge
    ) sp
    LEFT JOIN _debug_network net ON net.id = sp.edge;
END;
$$ LANGUAGE plpgsql;