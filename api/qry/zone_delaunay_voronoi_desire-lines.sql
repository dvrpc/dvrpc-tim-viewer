SELECT 
    edge, totalval,
    net.geom
FROM (
SELECT
    SUM(val) totalval,
    UNNEST(edge_array) edge
FROM (
    SELECT
        mtx.val,
        paths.edge_array
    FROM (
        SELECT
            -- seq, path_seq,
            end_vid,
            -- node,
            array_agg(edge) edge_array
            -- cost, agg_cost
        FROM pgr_dijkstra('
            SELECT id, source, target, length AS cost, length reverse_cost FROM gfx_zone_network
            WHERE
                ozone <> 401
            UNION ALL
            SELECT id, source, target, length AS cost, length reverse_cost FROM gfx_zone_network
            WHERE
                dzone <> 401
            UNION ALL
            SELECT id, source, target, length AS cost, length reverse_cost FROM gfx_zone_network
            WHERE
                nonconnector = 1
            UNION ALL
            SELECT id, source, target, length AS cost, 9e9 reverse_cost FROM gfx_zone_network
            WHERE
                ozone = 401
            UNION ALL
            SELECT id, source, target, 9e9 AS cost, length reverse_cost FROM gfx_zone_network
            WHERE
                dzone = 401
            ',
            401,
            (SELECT ARRAY_AGG(no) FROM (SELECT no FROM net_zone LIMIT 1000) sq)::INTEGER[],
            directed := true
        ) fn
        WHERE edge <> -1
        GROUP BY end_vid
    ) paths
    LEFT JOIN mtx_2000 mtx ON mtx.ozoneno = 401
        -- AND mtx.dzoneno = ANY((SELECT ARRAY_AGG(no) FROM (SELECT no FROM net_zone LIMIT 1000) sq)::INTEGER[])
        AND mtx.dzoneno = paths.end_vid
        AND mtx.tod = ANY(ARRAY['AM']::TEXT[])
) q
GROUP BY edge
) agg_paths
LEFT JOIN gfx_zone_network net ON net.id = agg_paths.edge

ORDER BY totalval