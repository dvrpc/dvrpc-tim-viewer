CREATE OR REPLACE FUNCTION tim_getschema()
RETURNS JSON AS $$
DECLARE
    retval JSON;
BEGIN

    SELECT
        json_agg(row_to_json(t)) INTO retval
    FROM (
        SELECT 
            tbl,
            array_agg(row_to_json((SELECT sq FROM (SELECT f, key) sq))) fields
        FROM (
            SELECT
                m.table_name::text tbl,
                m.column_name::text f,
                (CASE WHEN m_no.field IS NULL THEN FALSE ELSE TRUE END)::boolean AS key
            FROM meta m
            LEFT JOIN meta_netobj m_no
            ON m.table_name::text IN ('dat_' || m_no.netobj, 'net_' || m_no.netobj)
            AND m.column_name::text = m_no.field
            ORDER BY m.table_name::text, m.ordinal_position
        ) _q
        GROUP BY tbl
    ) t

    RETURN retval;
END;
$$ LANGUAGE plpgsql;