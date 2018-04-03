WITH _data AS (
SELECT * FROM data 
WHERE
    timestmp >= '2017-11-04 00:00'
AND timestmp <  '2017-11-05 00:00'
ORDER BY timestmp
),
joined AS (
SELECT
    -- *,
    timestmp::time,
    lines.line line,
    services.service service,
    trainnos.trainno trainno,
    consist,
    consistlength,
    origins.stop origin,
    destinations.stop destination,
    nextstops.stop nextstop,
    late,
    lat, lon,
    ST_SetSRID(ST_MakePoint(lon, lat), 4326) geom
FROM _data
LEFT JOIN lines ON lines.id = _data.line
LEFT JOIN services ON services.id = _data.service
LEFT JOIN trainnos ON trainnos.id = _data.trainno
LEFT JOIN stops origins ON origins.id = _data.origin
LEFT JOIN stops destinations ON destinations.id = _data.destination
LEFT JOIN stops nextstops ON nextstops.id = _data.nextstop
-- WHERE lines.line = 'Lansdale/Doylestown'
)
SELECT trainno, array_agg(DISTINCT(line))
-- ST_MakeLine(array_agg(geom)) geom
-- array_agg(ARRAY[lon, lat]::REAL[])
FROM joined
-- SEPTA Purgatory
WHERE NOT geom && ST_MakeEnvelope(-75.187003, 39.957494, -75.186891, 39.957575, 4326)
GROUP BY trainno
ORDER BY trainno