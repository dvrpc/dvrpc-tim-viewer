-- Replace tim_getskimbyzoneno

CREATE OR REPLACE FUNCTION tim_mtxvals(mtxno INTEGER, zonenos INTEGER[])
RETURNS TABLE(
    ozoneno INTEGER,
    dzoneno INTEGER,
    tod TEXT,
    val REAL
) AS $$
DECLARE
    _mtx_tbl TEXT;
BEGIN
    _mtx_tbl := FORMAT('%I', 'mtx_' || mtxno);
    
    RETURN QUERY
    SELECT * FROM mtx_1000
    WHERE ozoneno = ANY(ARRAY[401]::INTEGER[])
    OR dzoneno = ANY(ARRAY[401]::INTEGER[]);
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION tim_mtxvals_ct(mtxno INTEGER, zonenos INTEGER[])
RETURNS TABLE(
    odpair INTEGER[],
    AM REAL,
    MD REAL,
    PM REAL,
    NT REAL
) AS $$
DECLARE
    _mtx_tbl TEXT;
BEGIN
    _mtx_tbl := FORMAT('%I', 'mtx_' || mtxno);
    
    RETURN QUERY
    SELECT * FROM crosstab('
        SELECT
            ARRAY[ozoneno, dzoneno]::INTEGER[] odpair,
            tod,
            val
        FROM mtx_2000
        WHERE ozoneno = ANY(ARRAY[401,402]::INTEGER[])
        OR dzoneno = ANY(ARRAY[401,402]::INTEGER[])
        ORDER BY 1,2
    ') AS ct(
        odpair INTEGER[],
        AM REAL, MD REAL,
        PM REAL, NT REAL
    );
END;
$$ LANGUAGE plpgsql;