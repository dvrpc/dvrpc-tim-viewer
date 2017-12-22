CREATE OR REPLACE FUNCTION tim_netobjids(netobj TEXT)
RETURNS TEXT AS $$
DECLARE
    fields TEXT;
    tablename TEXT;
    f TEXT;
BEGIN
    tablename := FORMAT('net_%s', netobj);

    EXECUTE('
        SELECT array_to_string(array_agg(column_name::text), '','')
        FROM meta
        WHERE table_name = $1
        AND udt_name <> ''geometry''
    ') USING tablename INTO fields;

    -- Possible that the fields will need to be properly escaped
    -- FOR f IN (SELECT UNNEST(fields)) LOOP
    --     fields := array_append(fields, FORMAT('%I', f));
    -- END LOOP;

    RETURN FORMAT('%s', fields);
END;
$$ LANGUAGE plpgsql;