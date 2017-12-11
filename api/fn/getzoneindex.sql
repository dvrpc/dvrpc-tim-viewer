CREATE OR REPLACE FUNCTION tim_getzoneindex(zoneno INTEGER)
RETURNS integer AS $$
DECLARE
    zoneindex INTEGER;
BEGIN
    CREATE TEMPORARY TABLE no_index (_zoneindex INTEGER, _zoneno INTEGER) ON COMMIT DROP;
    INSERT INTO no_index SELECT (rownum - 1)::INTEGER zoneindex, no zoneno FROM (
        SELECT row_number() OVER (ORDER BY no NULLS LAST) rownum, no FROM tim23_zone ORDER BY no
    ) _q;
    CREATE INDEX no_index_zoneindex_idx ON no_index (_zoneindex ASC NULLS LAST);
    CREATE INDEX no_index_zoneno_idx ON no_index (_zoneno ASC NULLS LAST);
    SELECT ni._zoneindex INTO zoneindex FROM no_index ni WHERE ni._zoneno = zoneno;
    RETURN zoneindex;
END;
$$ LANGUAGE plpgsql;