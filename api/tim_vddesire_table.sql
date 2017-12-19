WITH
zone_index AS (
    SELECT indexp1 - 1 AS index, no
    FROM (
        SELECT row_number() OVER (ORDER BY no) AS indexp1, no
        FROM net_zones
    ) _q
)
SELECT sp.*, net.geom FROM (
    SELECT fn.edge, SUM(val) totalval
    FROM pgr_dijkstra('
        SELECT id, source, target, cost AS cost, rcost as reverse_cost
        FROM (
            SELECT id, source, target,
                fwd * length AS cost,
                rev * length AS rcost
            FROM (
                SELECT
                    id, source, target,
                    ST_Length(geom) length,
                    (ozone IS NULL AND dzone IS NULL)::integer tflag, -- Trunk Flag (always reverseable)
                CASE
                    WHEN ozone IS NULL AND dzone IS NULL THEN 1
                    WHEN ozone IS NULL THEN CASE
                        WHEN dzone = 135 THEN 999999
                        ELSE 1
                    END
                    ELSE CASE
                        WHEN ozone = 135 THEN 1
                        ELSE 999999
                    END
                END fwd,
                CASE
                    WHEN dzone IS NULL AND ozone IS NULL THEN 1
                    WHEN dzone IS NULL THEN CASE
                        WHEN ozone = 135 THEN 999999
                        ELSE 1
                    END
                    ELSE CASE
                        WHEN dzone = 135 THEN 1
                        ELSE 999999
                    END
                    END rev
                FROM _debug_network
            ) __q
        ) _q',
        16266,
        (SELECT array_agg(id) FROM _debug_network_zones WHERE no <> 135),
        directed := true
    ) fn
    LEFT JOIN _debug_network_zones z ON z.id = fn.end_vid
    LEFT JOIN zone_index zi ON z.no = zi.no
    LEFT JOIN mtx_2000_am mtx ON mtx.oindex = 134 AND mtx.dindex = zi.index
    GROUP BY fn.edge
) sp
LEFT JOIN _debug_network net ON net.id = sp.edge