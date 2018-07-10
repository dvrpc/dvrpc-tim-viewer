-- Dependencies:
--  table/gtfs_stop_times

WITH _st_timebounds AS (
SELECT
    gtfs_id,
    trip_id,
    min(arrival_time) origin_time,
    max(departure_time) destination_time
FROM gtfs_stop_times
-- WHERE gtfs_id = 1
GROUP BY gtfs_id, trip_id
)
SELECT 
    gtfs_id,
    min(origin_time) start_time,
    max(destination_time) end_time
FROM _st_timebounds
GROUP BY gtfs_id
ORDER BY gtfs_id