CREATE OR REPLACE FUNCTION tim_getskimbyzoneindex(zoneindex INTEGER, mtxno INTEGER)
RETURNS TABLE(
    oindex SMALLINT,
    dindex SMALLINT,
    am DOUBLE PRECISION,
    md DOUBLE PRECISION,
    pm DOUBLE PRECISION,
    nt DOUBLE PRECISION
) AS $$
DECLARE
    _am TEXT;
    _md TEXT;
    _pm TEXT;
    _nt TEXT;
BEGIN
    _am := format('%I', 'mtx_' || mtxno || '_am');
    _md := format('%I', 'mtx_' || mtxno || '_md');
    _pm := format('%I', 'mtx_' || mtxno || '_pm');
    _nt := format('%I', 'mtx_' || mtxno || '_nt');
    
    RETURN QUERY
    EXECUTE format('
    SELECT
        am.oindex, am.dindex,
        am.val am, md.val md,
        pm.val pm, nt.val nt
    FROM %I am
    INNER JOIN %I md
    ON am.oindex = md.oindex AND am.dindex = md.dindex
    INNER JOIN %I pm
    ON am.oindex = pm.oindex AND am.dindex = pm.dindex
    INNER JOIN %I nt
    ON am.oindex = nt.oindex AND am.dindex = nt.dindex
    WHERE am.oindex = $1

    UNION ALL

    SELECT
        am.oindex, am.dindex,
        am.val am, md.val md,
        pm.val pm, nt.val nt
    FROM %I am
    INNER JOIN %I md
    ON am.oindex = md.oindex AND am.dindex = md.dindex
    INNER JOIN %I pm
    ON am.oindex = pm.oindex AND am.dindex = pm.dindex
    INNER JOIN %I nt
    ON am.oindex = nt.oindex AND am.dindex = nt.dindex
    WHERE am.dindex = $1
    ', _am, _md, _pm, _nt, _am, _md, _pm, _nt) USING zoneindex;

END;

$$ LANGUAGE plpgsql;