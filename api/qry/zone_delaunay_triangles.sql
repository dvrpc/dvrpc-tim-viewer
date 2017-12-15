SELECT
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
ON st_intersects(dz.wktloc, endgeom)