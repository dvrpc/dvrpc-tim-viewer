CREATE OR REPLACE FUNCTION tim_getzoneindex(zoneno INTEGER)
RETURNS integer AS $$
DECLARE
    zoneindex INTEGER;
BEGIN
    SELECT
        indexp1 - 1 INTO zoneindex
    FROM (
        SELECT row_number() OVER (ORDER BY no) AS indexp1, *
        FROM net_zones
    ) _q
    WHERE _q.no = zoneno;
    RETURN zoneindex;
END;
$$ LANGUAGE plpgsql;