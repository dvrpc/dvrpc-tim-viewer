CREATE OR REPLACE FUNCTION tim_getzoneno(zoneindex INTEGER)
RETURNS INTEGER AS $$
DECLARE
    zoneno INTEGER;
BEGIN
    SELECT
        no INTO zoneno
    FROM (
        SELECT row_number() OVER (ORDER BY no) AS indexp1, *
        FROM net_zones
    ) _q
    WHERE _q.indexp1 - 1 = zoneindex;
    RETURN zoneno;
END;
$$ LANGUAGE plpgsql;