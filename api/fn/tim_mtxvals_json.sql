CREATE OR REPLACE FUNCTION tim_mtxvals_json (mtxno INTEGER, zonenos INTEGER[])
RETURNS json AS $$
DECLARE
    retval JSON;
BEGIN
    SELECT
        array_to_json(array_agg(row_to_json(_q))) INTO retval
    FROM (
    SELECT
        odpair od,
        row_to_json((SELECT r FROM (SELECT AM, MD, PM, NT) r)) vals
    FROM tim_mtxvals_ct(2000, ARRAY[1]::INTEGER[])
    ) _q;
    RETURN retval
END;
$$ LANGUAGE plpgsql;