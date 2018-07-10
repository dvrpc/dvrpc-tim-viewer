WITH _data AS (
    SELECT
        *, ST_SetSRID(ST_MakePoint(lon, lat), 4326) geom
    FROM trainview_joined
    WHERE
        tstz >= '2017-11-04 00:00'
    AND tstz <  '2017-11-05 00:00'
    ORDER BY tstz
)
SELECT trainno, array_agg(DISTINCT(line))
-- ST_MakeLine(array_agg(geom)) geom
-- array_agg(ARRAY[lon, lat]::REAL[])
FROM _data
-- SEPTA Purgatory
WHERE NOT geom && ST_MakeEnvelope(-75.187003, 39.957494, -75.186891, 39.957575, 4326)
GROUP BY trainno
ORDER BY trainno
