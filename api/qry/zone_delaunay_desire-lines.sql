WITH
_zones AS (
    SELECT no, indexp1 - 1 AS index
    FROM (
        SELECT *, row_number() OVER (ORDER BY no) AS indexp1
        FROM net_zones
    ) _q
),
_trgt AS (
    SELECT index
    FROM _zones
    WHERE no = 135
),
_mtx1 AS (
    SELECT mtx.*, _zones.no AS dno
    FROM mtx_428_am mtx
    LEFT JOIN _zones ON _zones.index = dindex
    WHERE oindex IN (SELECT * FROM _trgt)
)
SELECT *
FROM (
    SELECT edge, SUM(val) totalval
    FROM pgr_dijkstra(
        'SELECT id, ozone source, dzone target, length AS cost, length as reverse_cost FROM gfx_zone_delaunay',
        135,
        (SELECT array_agg(no) FROM net_zones WHERE no <> 135),
        directed := false
    ) fn
    LEFT JOIN _mtx1 ON _mtx1.dno = fn.end_vid
    GROUP BY edge
) _q
LEFT JOIN gfx_zone_delaunay d
ON d.id = edge
WHERE totalval IS NOT NULL