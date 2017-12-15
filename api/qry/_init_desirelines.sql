DROP TABLE IF EXISTS _debug_voronoi;
DROP TABLE IF EXISTS _debug_voronoi_vertices_pgr;
CREATE TABLE _debug_voronoi AS SELECT (row_number() OVER ())::integer AS id, (geodump).geom, NULL::integer source, NULL::integer target FROM (SELECT ST_Dump(ST_VoronoiLines(ST_Collect(wktloc))) geodump FROM geom_zones) _q;
CREATE INDEX IF NOT EXISTS _debug_voronoi_gidx ON _debug_voronoi USING GIST (geom);
CREATE INDEX IF NOT EXISTS _debug_delaunay_gidx ON _debug_delaunay USING GIST (geom);
DROP TABLE IF EXISTS _debug_network;
DROP TABLE IF EXISTS _debug_network_vertices_pgr;
CREATE TABLE _debug_network AS (
SELECT row_number() OVER () AS id, * FROM (
WITH
DxV AS (
SELECT d.id did, ST_Dump(ST_Split(d.geom, _d.geom)) geodump FROM _debug_delaunay d INNER JOIN (
SELECT d.id did, ST_Collect(v.geom) geom FROM _debug_delaunay d JOIN _debug_voronoi v ON d.geom && v.geom GROUP BY d.id
)_d ON d.id = _d.did
),
VxD AS (
SELECT v.id vid, ST_Dump(ST_Split(v.geom, _v.geom)) geodump FROM _debug_voronoi v INNER JOIN (
SELECT v.id vid, ST_Collect(d.geom) geom FROM _debug_voronoi v JOIN _debug_delaunay d ON v.geom && d.geom GROUP BY v.id
) _v ON v.id = _v.vid
)
SELECT did, NULL vid, (geodump).geom, NULL::integer source, NULL::integer target FROM DxV UNION ALL
SELECT NULL did, vid, (geodump).geom, NULL::integer source, NULL::integer target FROM VxD UNION ALL
SELECT NULL did, v.id vid, v.geom, NULL::integer source, NULL::integer target
FROM _debug_voronoi v
WHERE v.id NOT IN (SELECT DISTINCT(vid) FROM VxD)) _q);

CREATE INDEX IF NOT EXISTS _debug_network_gidx ON _debug_network USING GIST (geom);
SELECT pgr_createTopology('_debug_network', 0.0001, 'geom', 'id');

SELECT COUNT(*) FROM _debug_network_vertices_pgr;