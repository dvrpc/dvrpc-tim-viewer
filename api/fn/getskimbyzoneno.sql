CREATE OR REPLACE FUNCTION tim_getskimbyzoneno(zoneno INTEGER, mtxno INTEGER)
RETURNS TABLE(
    ozoneno INTEGER,
    dzoneno INTEGER,
    am DOUBLE PRECISION,
    md DOUBLE PRECISION,
    pm DOUBLE PRECISION,
    nt DOUBLE PRECISION
) AS $$
DECLARE
    zoneindex INTEGER;
    _am TEXT;
    _md TEXT;
    _pm TEXT;
    _nt TEXT;
BEGIN
    _am := format('%I', 'mtx_' || mtxno || '_am');
    _md := format('%I', 'mtx_' || mtxno || '_md');
    _pm := format('%I', 'mtx_' || mtxno || '_pm');
    _nt := format('%I', 'mtx_' || mtxno || '_nt');

    CREATE TEMPORARY TABLE no_index (_zoneindex INTEGER, _zoneno INTEGER) ON COMMIT DROP;
    INSERT INTO no_index SELECT (rownum - 1)::INTEGER zoneindex, no zoneno FROM (
        SELECT row_number() OVER (ORDER BY no NULLS LAST) rownum, no FROM tim23_zone ORDER BY no
    ) _q;
    CREATE INDEX no_index_zoneindex_idx ON no_index (_zoneindex ASC NULLS LAST);
    CREATE INDEX no_index_zoneno_idx ON no_index (_zoneno ASC NULLS LAST);
    SELECT ni._zoneindex INTO zoneindex FROM no_index ni WHERE ni._zoneno = zoneno;

    RETURN QUERY
    EXECUTE format('
    SELECT
        ni_o._zoneno, ni_d._zoneno,
        am.val am, md.val md,
        pm.val pm, nt.val nt
    FROM %I am
    INNER JOIN %I md
    ON am.oindex = md.oindex AND am.dindex = md.dindex
    INNER JOIN %I pm
    ON am.oindex = pm.oindex AND am.dindex = pm.dindex
    INNER JOIN %I nt
    ON am.oindex = nt.oindex AND am.dindex = nt.dindex
    LEFT JOIN no_index ni_o
    ON am.oindex = ni_o._zoneindex
    LEFT JOIN no_index ni_d
    ON am.dindex = ni_d._zoneindex
    WHERE am.oindex = $1

    UNION ALL

    SELECT
        ni_o._zoneno, ni_d._zoneno,
        am.val am, md.val md,
        pm.val pm, nt.val nt
    FROM %I am
    INNER JOIN %I md
    ON am.oindex = md.oindex AND am.dindex = md.dindex
    INNER JOIN %I pm
    ON am.oindex = pm.oindex AND am.dindex = pm.dindex
    INNER JOIN %I nt
    ON am.oindex = nt.oindex AND am.dindex = nt.dindex
    LEFT JOIN no_index ni_o
    ON am.oindex = ni_o._zoneindex
    LEFT JOIN no_index ni_d
    ON am.dindex = ni_d._zoneindex
    WHERE am.dindex = $1
    ', _am, _md, _pm, _nt, _am, _md, _pm, _nt) USING zoneindex;

END;

$$ LANGUAGE plpgsql;