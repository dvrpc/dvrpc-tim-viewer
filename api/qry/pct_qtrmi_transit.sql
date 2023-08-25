-- Buffer Stop Points, Intersect with Zones
DROP TABLE IF EXISTS _temp_geom_zones;
DROP TABLE IF EXISTS _temp_geom_stoppoints;
CREATE TABLE IF NOT EXISTS _temp_geom_zones AS
    SELECT no, ST_MakeValid(ST_Transform(wktsurface, 26918)) wktsurface FROM geom_zones
    WHERE ST_Area(wktsurface) > 0;
CREATE INDEX IF NOT EXISTS _temp_geom_zones_gidx ON _temp_geom_zones USING GIST(wktsurface);
CREATE TABLE IF NOT EXISTS _temp_geom_stoppoints AS
    SELECT ST_MakeValid(ST_Union(wktloc)) geom FROM (
        SELECT ST_Buffer(ST_Transform(wktloc, 26918), 402.336) wktloc
        FROM geom_stoppoints
    ) q;
CREATE INDEX IF NOT EXISTS _temp_geom_stoppoints_gidx ON _temp_geom_stoppoints USING GIST(geom);

ALTER TABLE net_zones DROP COLUMN IF EXISTS pct_qtrmi_transit;
ALTER TABLE net_zones ADD COLUMN IF NOT EXISTS pct_qtrmi_transit DOUBLE PRECISION;

UPDATE net_zones 
SET pct_qtrmi_transit = q.pct
FROM (
    SELECT 
        gz.no,
        SUM(COALESCE(
            (ST_Area(ST_Intersection(gz.wktsurface, gsp.geom))/ST_Area(gz.wktsurface)),
        0)) pct
    FROM _temp_geom_zones gz
    LEFT JOIN _temp_geom_stoppoints gsp
    ON TRUE
    -- ON ST_Overlaps(gz.wktsurface, gsp.geom) OR ST_Overlaps(gsp.geom, gz.wktsurface)
    GROUP BY gz.no
) q
WHERE net_zones.no = q.no;

DROP TABLE IF EXISTS _temp_geom_zones;
DROP TABLE IF EXISTS _temp_geom_stoppoints;

-- Buffer Zones, Intersect with Stop Points
DROP TABLE IF EXISTS _temp_geom_zones_26918;
DROP TABLE IF EXISTS _temp_geom_stoppoints_26918;
CREATE TABLE _temp_geom_zones_26918 AS
SELECT no, ST_Buffer(ST_Transform(wktsurface, 26918), 402.336) wktsurface FROM geom_zones;
CREATE INDEX _temp_geom_zones_26918_gidx ON _temp_geom_zones_26918 USING GIST(wktsurface);
CREATE TABLE _temp_geom_stoppoints_26918 AS
SELECT no, ST_Transform(wktloc, 26918) wktloc FROM geom_stoppoints;
CREATE INDEX _temp_geom_stoppoints_26918_gidx ON _temp_geom_stoppoints_26918 USING GIST(wktloc);
SELECT gz.no, COUNT(*) FROM _temp_geom_zones_26918 gz INNER JOIN _temp_geom_stoppoints_26918 gsp
ON ST_Within(gsp.wktloc, gz.wktsurface) GROUP BY gz.no ORDER BY gz.no;