DROP TABLE IF EXISTS _temp_geom_zones;
CREATE TABLE _temp_geom_zones AS
SELECT no, 
    ST_Transform(
        ST_Buffer(
            ST_Transform(wktsurface, 26918),
            1609.344
        ),
        4326
    ) wktsurface
FROM geom_zones;
CREATE INDEX _temp_geom_zones_gidx ON _temp_geom_zones USING GIST(wktsurface);

ALTER TABLE net_zones DROP COLUMN IF EXISTS emp_1mi;
ALTER TABLE net_zones ADD COLUMN IF NOT EXISTS emp_1mi INTEGER;

UPDATE net_zones
SET emp_1mi = q.emp_1mi
FROM (
WITH _od_pairs AS (
    SELECT gz.no ozoneno, tgz.no dzoneno
    FROM geom_zones gz
    LEFT JOIN _temp_geom_zones tgz
    ON ST_Intersects(gz.wktsurface, tgz.wktsurface)
)
SELECT odp.ozoneno, SUM(nz.total_employment) emp_1mi
FROM _od_pairs odp 
LEFT JOIN net_zones nz ON odp.dzoneno = nz.no
GROUP BY odp.ozoneno
) q
WHERE net_zones.no = q.no;

DROP TABLE IF EXISTS _temp_geom_zones;