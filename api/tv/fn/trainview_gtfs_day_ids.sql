CREATE OR REPLACE FUNCTION trainview_gtfs_day_ids (isodate TEXT)
RETURNS TABLE (
    gtfs_id SMALLINT,
    service_id TEXT
) AS $$
BEGIN
    RETURN QUERY
    WITH cal AS (
        SELECT
            _cal.gtfs_id,
            _cal.service_id,
            start_date,
            end_date,
            (
                row_to_json(
                    (SELECT d FROM (SELECT monday, tuesday, wednesday, thursday, friday, saturday, sunday) d)
                ) ->> trim(both ' ' FROM TO_CHAR(isodate::timestamp, 'day'))
            )::smallint valid_service_id
        FROM gtfs_calendar _cal
        WHERE
            start_date <= isodate::timestamp
        AND end_date >= isodate::timestamp  + '1 day'::interval
    ),
    sel_gtfs_service_ids AS (
        SELECT max(cal.gtfs_id) gtfs_id FROM cal WHERE valid_service_id = 1
    )
    SELECT cal.gtfs_id, cal.service_id FROM sel_gtfs_service_ids _sel
    LEFT JOIN cal
    ON cal.gtfs_id = _sel.gtfs_id
    WHERE cal.valid_service_id = 1;
END;
$$ LANGUAGE plpgsql;