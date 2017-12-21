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

-- Create meta view
CREATE VIEW meta AS
SELECT table_name, column_name, ordinal_position, data_type, udt_name
FROM information_schema.columns isc
LEFT JOIN pg_tables pgt
ON isc.table_name = pgt.tablename
WHERE pgt.schemaname = 'public'
AND pgt.tablename IS NOT NULL
AND pgt.tablename <> 'spatial_ref_sys'
ORDER BY table_name, ordinal_position