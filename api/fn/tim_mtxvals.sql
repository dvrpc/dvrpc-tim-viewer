-- Replace tim_getskimbyzoneno

CREATE OR REPLACE FUNCTION tim_mtxvals(mtxno INTEGER, zonenos INTEGER[])
RETURNS TABLE (
    ozoneno INTEGER,
    dzoneno INTEGER,
    tod TEXT,
    val DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM tim_mtxvals(mtxno, zonenos, ARRAY['AM','MD','PM','NT']::TEXT[]);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION tim_mtxvals(mtxno INTEGER, zonenos INTEGER[], tods TEXT[])
RETURNS TABLE (
    ozoneno INTEGER,
    dzoneno INTEGER,
    tod TEXT,
    val DOUBLE PRECISION
) AS $$
DECLARE
    _mtx_tbl TEXT;
BEGIN
    _mtx_tbl := FORMAT('%I', 'mtx_' || mtxno);
    
    RETURN QUERY
    EXECUTE FORMAT('
    SELECT * FROM %I
    WHERE tod = ANY($1::TEXT[])
    AND (ozoneno = ANY($2::INTEGER[])
    OR dzoneno = ANY($2::INTEGER[]));
    ', _mtx_tbl) USING tods, zonenos;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION tim_mtxvals_ct(mtxno INTEGER, zonenos INTEGER[])
RETURNS TABLE(
    odpair INTEGER[],
    AM DOUBLE PRECISION,
    MD DOUBLE PRECISION,
    PM DOUBLE PRECISION,
    NT DOUBLE PRECISION
) AS $$
DECLARE
    _mtx_tbl TEXT;
BEGIN
    _mtx_tbl := FORMAT('%I', 'mtx_' || mtxno);
    
    RETURN QUERY
    SELECT * FROM crosstab(FORMAT('
        SELECT
            ARRAY[ozoneno, dzoneno]::INTEGER[] odpair,
            tod,
            val
        FROM %I
        WHERE ozoneno = ANY(%L::INTEGER[])
        OR dzoneno = ANY(%L::INTEGER[])
        ORDER BY 1,2
    ', _mtx_tbl, zonenos, zonenos)) AS ct(
        odpair INTEGER[],
        AM DOUBLE PRECISION, MD DOUBLE PRECISION,
        PM DOUBLE PRECISION, NT DOUBLE PRECISION
    );
END;
$$ LANGUAGE plpgsql;
