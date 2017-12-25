CREATE OR REPLACE FUNCTION tim_getschema()
RETURNS JSON AS $$
DECLARE
    retval JSON;
BEGIN
    SELECT json_agg(row_to_json(_q)) INTO retval
    FROM (
        SELECT table_name::text t, array_agg(column_name::text) fs
        FROM meta GROUP BY table_name
    ) _q;
    RETURN retval;
END;
$$ LANGUAGE plpgsql;