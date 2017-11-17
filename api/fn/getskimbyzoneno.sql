CREATE OR REPLACE FUNCTION getskimbyzoneno(zoneno INTEGER, mtxno INTEGER)
RETURNS TABLE(
    oindex INTEGER,
    dindex INTEGER,
    am DOUBLE PRECISION,
    md DOUBLE PRECISION,
    pm DOUBLE PRECISION,
    nt DOUBLE PRECISION
) AS $$
DECLARE
    zoneindex INTEGER;
BEGIN

    SELECT (rownum - 1)::INTEGER INTO zoneindex
    FROM (
        SELECT row_number() OVER (ORDER BY no NULLS LAST) rownum, no
        FROM tim23_zone ORDER BY no
    ) _q WHERE no = zoneno;

    CREATE TEMPORARY TABLE _am (oindex INTEGER, dindex INTEGER, val DOUBLE PRECISION) ON COMMIT DROP;
    CREATE TEMPORARY TABLE _md (oindex INTEGER, dindex INTEGER, val DOUBLE PRECISION) ON COMMIT DROP;
    CREATE TEMPORARY TABLE _pm (oindex INTEGER, dindex INTEGER, val DOUBLE PRECISION) ON COMMIT DROP;
    CREATE TEMPORARY TABLE _nt (oindex INTEGER, dindex INTEGER, val DOUBLE PRECISION) ON COMMIT DROP;

    EXECUTE format('INSERT INTO _am SELECT oindex, dindex, val FROM %I WHERE oindex = $1 OR dindex = $1', 'mtx_' || mtxno || '_am') USING zoneindex;
    EXECUTE format('INSERT INTO _md SELECT oindex, dindex, val FROM %I WHERE oindex = $1 OR dindex = $1', 'mtx_' || mtxno || '_md') USING zoneindex;
    EXECUTE format('INSERT INTO _pm SELECT oindex, dindex, val FROM %I WHERE oindex = $1 OR dindex = $1', 'mtx_' || mtxno || '_pm') USING zoneindex;
    EXECUTE format('INSERT INTO _nt SELECT oindex, dindex, val FROM %I WHERE oindex = $1 OR dindex = $1', 'mtx_' || mtxno || '_nt') USING zoneindex;

    RETURN QUERY
    SELECT
        _am.oindex, _am.dindex,
        _am.val am, _md.val md,
        _pm.val pm, _nt.val nt
    FROM _am
    INNER JOIN _md
    ON _am.oindex = _md.oindex AND _am.dindex = _md.dindex
    INNER JOIN _pm
    ON _am.oindex = _pm.oindex AND _am.dindex = _pm.dindex
    INNER JOIN _nt
    ON _am.oindex = _nt.oindex AND _am.dindex = _nt.dindex
    WHERE _am.oindex = zoneindex
    
    UNION ALL
    
    SELECT
        _am.oindex, _am.dindex,
        _am.val am, _md.val md,
        _pm.val pm, _nt.val nt
    FROM _am
    INNER JOIN _md
    ON _am.oindex = _md.oindex AND _am.dindex = _md.dindex
    INNER JOIN _pm
    ON _am.oindex = _pm.oindex AND _am.dindex = _pm.dindex
    INNER JOIN _nt
    ON _am.oindex = _nt.oindex AND _am.dindex = _nt.dindex
    WHERE _am.dindex = zoneindex;

END;
$$ LANGUAGE plpgsql;