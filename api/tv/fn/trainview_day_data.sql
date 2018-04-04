CREATE OR REPLACE FUNCTION trainview_day_data (isodate TEXT)
RETURNS TABLE (
    timestmp TIMESTAMP,
    line TEXT,
    service TEXT,
    trainno TEXT,
    consist TEXT[],
    consistlength SMALLINT,
    origin TEXT,
    destination TEXT,
    nextstop TEXT,
    late SMALLINT,
    lat REAL,
    lon REAL
) AS $$
BEGIN
    RETURN QUERY
    WITH _data AS (
        SELECT * FROM data d
        WHERE
            d.timestmp >= (isodate::timestamp)
        AND d.timestmp <  (isodate::timestamp + '36 hours'::interval)
        ORDER BY d.timestmp
    )
    SELECT
        _data.timestmp,
        lines.line line,
        services.service service,
        trainnos.trainno trainno,
        _data.consist,
        _data.consistlength,
        origins.stop origin,
        destinations.stop destination,
        nextstops.stop nextstop,
        _data.late,
        _data.lat, _data.lon
    FROM _data
    LEFT JOIN lines ON lines.id = _data.line
    LEFT JOIN services ON services.id = _data.service
    LEFT JOIN trainnos ON trainnos.id = _data.trainno
    LEFT JOIN stops origins ON origins.id = _data.origin
    LEFT JOIN stops destinations ON destinations.id = _data.destination
    LEFT JOIN stops nextstops ON nextstops.id = _data.nextstop;
END;
$$ LANGUAGE plpgsql;