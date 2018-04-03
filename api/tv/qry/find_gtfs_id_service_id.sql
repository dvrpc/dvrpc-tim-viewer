WITH cal AS (
    SELECT
        gtfs_id,
        service_id,
        start_date,
        end_date,
        (
            row_to_json(
                (SELECT d FROM (SELECT monday, tuesday, wednesday, thursday, friday, saturday, sunday) d)
            ) ->> trim(both ' ' FROM TO_CHAR('2017-11-03 00:00'::timestamp, 'day'))
        )::smallint valid_service_id
    FROM gtfs_calendar
    WHERE
        start_date <= '2017-11-03 00:00'::timestamp
    AND end_date >= '2017-11-03 00:00'::timestamp  + '1 day'::interval
),
sel_gtfs_service_ids AS (
    SELECT max(gtfs_id) gtfs_id FROM cal WHERE valid_service_id = 1
)
SELECT cal.* FROM sel_gtfs_service_ids _sel
LEFT JOIN cal
ON cal.gtfs_id = _sel.gtfs_id
WHERE cal.valid_service_id = 1