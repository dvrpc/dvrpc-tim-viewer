CREATE OR REPLACE FUNCTION tim_vddesire_table (
    mtxno INTEGER,
    origzoneno INTEGER,
    destzonenos INTEGER[],
    tods TEXT[]
)
RETURNS TABLE (
    edge BIGINT,
    totalval REAL,
    geom GEOMETRY(LINESTRING, 4326)
) AS $$
DECLARE
    _mtx_tbl TEXT;
    origzoneid INTEGER;
    destzoneids INTEGER[];
BEGIN
    _mtx_tbl := FORMAT('%I', 'mtx_' || mtxno);

    SELECT id INTO origzoneid
    FROM gfx_zone_network_zones
    WHERE no = origzoneno;

    SELECT array_agg(id) INTO destzoneids
    FROM gfx_zone_network_zones
    WHERE no = ANY(destzonenos);

    RETURN QUERY
    EXECUTE FORMAT('
    SELECT sp.*, net.geom FROM (
        SELECT fn.edge, SUM(val) totalval
        FROM pgr_dijkstra(''
            SELECT id, source, target, length AS cost, length reverse_cost FROM gfx_zone_network
            WHERE
                ozone <> %s
            UNION ALL
            SELECT id, source, target, length AS cost, length reverse_cost FROM gfx_zone_network
            WHERE
                dzone <> %s
            UNION ALL
            SELECT id, source, target, length AS cost, length reverse_cost FROM gfx_zone_network
            WHERE
                nonconnector = 1
            UNION ALL
            SELECT id, source, target, length AS cost, 9e9 reverse_cost FROM gfx_zone_network
            WHERE
                ozone = %s
            UNION ALL
            SELECT id, source, target, 9e9 AS cost, length reverse_cost FROM gfx_zone_network
            WHERE
                dzone = %s
            '',
            $1,
            $2,
            directed := true
        ) fn
        LEFT JOIN gfx_zone_network_zones z ON z.id = fn.end_vid
        LEFT JOIN %I mtx ON mtx.ozoneno = $3 AND mtx.tod = ANY($4) AND mtx.dzoneno = z.no
        GROUP BY fn.edge
    ) sp
    LEFT JOIN gfx_zone_network net ON net.id = sp.edge
    WHERE net.geom IS NOT NULL;
    ', origzoneno, origzoneno, origzoneno, origzoneno, _mtx_tbl)
    USING origzoneid, destzoneids, origzoneno, tods;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION tim_vddesire_table(
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
        SELECT tim_vddesire_table(matrixno, origzoneno, destzonenos, tods) rec
        FROM (SELECT UNNEST(origzonenos) origzoneno) _q
    ) _q
    GROUP BY (_q.rec).edge, (_q.rec).geom;
END;
$$ LANGUAGE plpgsql;
