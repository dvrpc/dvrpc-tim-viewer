zoneno
zoneindex
zonevid

-- STATIC (Function zone)
-- 
CREATE TEMPORARY TABLE 
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
) _q

WITH zone_index AS (SELECT indexp1 - 1 AS index, no FROM (SELECT row_number() OVER (ORDER BY no) AS indexp1, no FROM net_zones) _q)
SELECT _q0.*, n.geom FROM (
SELECT _q1.edge, SUM(val) totalval
FROM (
SELECT fn.*, z.no, zi.index, mtx_2000_am.val
FROM pgr_dijkstra(
	'SELECT id, source, target, cost AS cost, rcost as reverse_cost FROM _debug_net',
	16266,
	(SELECT array_agg(DISTINCT(target)) FROM _debug_net WHERE dzone <> 16266),
	directed := true
) fn
LEFT JOIN _debug_network_zones z ON z.id = fn.end_vid
LEFT JOIN zone_index zi ON z.no = zi.no
LEFT JOIN mtx_2000_am ON oindex = 134 AND dindex = zi.index
) _q1
GROUP BY _q1.edge
) _q0
LEFT JOIN _debug_net n ON _q0.edge = n.id
