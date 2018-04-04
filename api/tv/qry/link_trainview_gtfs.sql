WITH gtfst AS (
SELECT trip_short_name, array_agg(route_id), min(start_time) start_time, max(end_time) end_time FROM trainview_gtfs_day_trips('2018-02-05 00:00:00') gtfst
GROUP BY trip_short_name
),
_ultra AS (
SELECT
    tvd.*,
    ('2018-02-05 00:00:00'::timestamp + gtfst.start_time) astart_time,
    ('2018-02-05 00:00:00'::timestamp + gtfst.end_time) aend_time
FROM trainview_day_data('2018-02-05 00:00:00') tvd
INNER JOIN gtfst
ON tvd.trainno = gtfst.trip_short_name
)
SELECT * FROM _ultra
WHERE
    timestmp > (astart_time - '1 hour'::interval)
AND timestmp < (aend_time + '4 hours'::interval)
AND trainno = '598'
