-- Note: Is this still needed?

-- Dependencies:
--  view/trainview_joined

CREATE OR REPLACE FUNCTION trainview_day_data (isodate TEXT)
RETURNS TABLE (
    tstz TIMESTAMPTZ,
    line TEXT,
    service TEXT,
    trainno TEXT,
    consist TEXT[],
    origstop TEXT,
    deststop TEXT,
    nextstop TEXT,
    heading REAL,
    late INTEGER,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.tstz,
        d.line,
        d.service,
        d.trainno,
        d.consist,
        d.origstop,
        d.deststop,
        d.nextstop,
        d.heading,
        d.late,
        d.lat,
        d.lon
    FROM trainview_joined d
    WHERE
        d.tstz >= (isodate::timestamp)
    AND d.tstz <  (isodate::timestamp + '36 hours'::interval)
    ORDER BY d.tstz;
END;
$$ LANGUAGE plpgsql;