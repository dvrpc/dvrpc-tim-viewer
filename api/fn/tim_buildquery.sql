CREATE OR REPLACE FUNCTION _debug_agg_json(netobj TEXT)
RETURNS TABLE(uid JSON) AS $$
DECLARE
    fields TEXT;
    tablename TEXT;
    f TEXT;
BEGIN
    tablename := FORMAT('%s', netobj);

    EXECUTE(FORMAT('
        SELECT array_to_string(array_agg(column_name::text), '','')
        FROM meta
        WHERE table_name = %I
        AND udt_name <> ''geometry''
    ', tablename)) INTO fields;

    FOR f IN (SELECT UNNEST(fields)) LOOP
    fields := array_append(fields, FORMAT('%I', f));
    END LOOP;

    RAISE NOTICE '%', FORMAT('SELECT %s FROM %I', fields, tablename);
    RETURN QUERY
    SELECT array_to_json(array_agg(fa)) FROM temp;
END;
$$ LANGUAGE plpgsql;