DROP TABLE IF EXISTS _debug_delaunay;
DROP TABLE IF EXISTS _debug_voronoi;
DROP TABLE IF EXISTS _debug_network;
DROP TABLE IF EXISTS _debug_network_vertices_pgr;
DROP TABLE IF EXISTS _debug_network_zones;

CREATE TABLE _debug_delaunay AS
SELECT
    (row_number() OVER ())::integer id,
    oz.no ozone,
    dz.no dzone,
    st_length(_q2.geom) length,
    _q2.geom
FROM (
    SELECT
        (geodump).geom geom,
        st_startpoint((geodump).geom) startgeom,
        st_endpoint((geodump).geom) endgeom
        FROM (
            SELECT ST_Dump(
                ST_DelaunayTriangles(
                    ST_Collect(
                        WKTLoc
                    ),
                    flags := 1
                )
            ) geodump
            FROM geom_zones
        ) _q1
) _q2
LEFT JOIN geom_zones oz
ON st_intersects(oz.wktloc, startgeom)
LEFT JOIN geom_zones dz
ON st_intersects(dz.wktloc, endgeom);
CREATE INDEX IF NOT EXISTS _debug_delaunay_gidx ON _debug_delaunay USING GIST (geom);

CREATE TABLE _debug_voronoi AS
SELECT
    (row_number() OVER ())::integer id,
    (geodump).geom,
    NULL::integer source,
    NULL::integer target
FROM (
    SELECT ST_Dump(ST_VoronoiLines(ST_Collect(wktloc))) geodump
    FROM geom_zones
) _q;
CREATE INDEX IF NOT EXISTS _debug_voronoi_gidx ON _debug_voronoi USING GIST (geom);

CREATE TABLE _debug_network AS
SELECT
    (row_number() OVER ())::integer id,
    *,
    NULL::integer ozone,
    NULL::integer dzone
FROM (
    WITH
    -- Delaunay cut by Voronoi
    DxV AS (
        SELECT d.id did, ST_Dump(ST_Split(d.geom, _d.geom)) geodump
        FROM _debug_delaunay d
        INNER JOIN (
            SELECT d.id did, ST_Collect(v.geom) geom
            FROM _debug_delaunay d
            JOIN _debug_voronoi v
            ON d.geom && v.geom
            GROUP BY d.id
        )_d ON d.id = _d.did
    ),
    -- Voronoi cut by Delaunay
    VxD AS (
        SELECT v.id vid, ST_Dump(ST_Split(v.geom, _v.geom)) geodump
        FROM _debug_voronoi v
        INNER JOIN (
            SELECT v.id vid, ST_Collect(d.geom) geom
            FROM _debug_voronoi v
            JOIN _debug_delaunay d
            ON v.geom && d.geom
            GROUP BY v.id
        ) _v ON v.id = _v.vid
    )
    SELECT did, NULL vid, (geodump).geom, NULL::integer source, NULL::integer target FROM DxV UNION ALL
    SELECT NULL did, vid, (geodump).geom, NULL::integer source, NULL::integer target FROM VxD UNION ALL
    SELECT NULL did, v.id vid, v.geom, NULL::integer source, NULL::integer target
    FROM _debug_voronoi v
    WHERE v.id NOT IN (SELECT DISTINCT(vid) FROM VxD)
) _q;
CREATE INDEX IF NOT EXISTS _debug_network_gidx ON _debug_network USING GIST (geom);

SELECT pgr_createTopology('_debug_network', 0.000001, 'geom', 'id');

CREATE TABLE _debug_network_zones AS SELECT n.id, z.no FROM _debug_network_vertices_pgr n JOIN geom_zones z ON z.wktloc = n.the_geom ORDER BY n.id;

-- Update network table with zone identifiers (if applicable)
UPDATE _debug_network
SET ozone = z.no
FROM _debug_network_vertices_pgr n JOIN geom_zones z ON z.wktloc = n.the_geom
WHERE source = n.id;

UPDATE _debug_network
SET dzone = z.no
FROM _debug_network_vertices_pgr n JOIN geom_zones z ON z.wktloc = n.the_geom
WHERE target = n.id;

-- STATIC (Function zone)
-- 
SELECT *,
    (tflag * length) + (o_out * length) + (d_in * length) AS cost,
    (tflag * length) + (o_in * length) + (d_out * length) AS rcost
FROM (
SELECT *,
    ST_Length(geom) length,
    (ozone IS NULL AND dzone IS NULL)::integer tflag, -- Trunk Flag (always reverseable)
    CASE
        WHEN ozone = 135 THEN 1
        WHEN dzone = 135 THEN 999999
        ELSE 0
    END o_out,
    CASE
        WHEN dzone = 135 THEN 1
        WHEN ozone = 135 THEN 999999
        ELSE 0
    END o_in,

    CASE 
        WHEN ozone IS NULL AND dzone IS NOT NULL THEN
            CASE WHEN dzone = 135 THEN 1
            ELSE 999999
        ELSE 0
    END d_in,
    CASE 
        WHEN dzone IS NULL AND ozone IS NOT NULL THEN 1
        ELSE 0
    END d_out

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
