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
                    FROM gfx_zone_network
                ) __q
            ) _q'',
            $1,
            $2,
            directed := true
        ) fn
        LEFT JOIN gfx_zone_network_zones z ON z.id = fn.end_vid
        LEFT JOIN %I mtx ON mtx.ozoneno = $3 AND mtx.dzoneno = ANY($4)
        GROUP BY fn.edge
    ) sp
    LEFT JOIN gfx_zone_network net ON net.id = sp.edge
    WHERE net.geom IS NOT NULL;
    ', origzoneno, origzoneno, origzoneno, origzoneno, _mtx_tbl)
    USING origzoneid, destzoneids, origzoneno, destzonenos;
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
