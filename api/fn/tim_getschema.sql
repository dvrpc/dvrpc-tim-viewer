CREATE OR REPLACE FUNCTION tim_getschema()
RETURNS JSON AS $$
DECLARE
    retval JSON;
BEGIN

    SELECT
        json_agg(row_to_json(_q1)) INTO retval
    FROM (
        SELECT 
            t,
            array_agg(row_to_json((SELECT sq FROM (SELECT f, key) sq))) fs
        FROM (
            SELECT
                m.table_name::text t,
                m.column_name::text f,
                (CASE WHEN m_no.field IS NULL THEN FALSE ELSE TRUE END)::boolean AS key
            FROM meta m
            LEFT JOIN tim_netobj_keys m_no
            ON m.table_name::text IN ('dat_' || m_no.netobj, 'net_' || m_no.netobj)
            AND m.column_name::text = m_no.field
            ORDER BY m.table_name::text, m.ordinal_position
        ) _q0
        GROUP BY t
    ) _q1;

    RETURN retval;
END;
$$ LANGUAGE plpgsql;