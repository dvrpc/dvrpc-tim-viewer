CREATE OR REPLACE FUNCTION tim_netobjids(netobj TEXT)
RETURNS TEXT AS $$
DECLARE
    fields TEXT;
    f TEXT;
BEGIN
    EXECUTE('
        SELECT array_to_string(array_agg(field), '','')
        FROM tim_netobj_keys
        WHERE netobj = $1
    ') USING netobj INTO fields;

    -- Possible that the fields will need to be properly escaped
    -- FOR f IN (SELECT UNNEST(fields)) LOOP
    --     fields := array_append(fields, FORMAT('%I', f));
    -- END LOOP;

    RETURN FORMAT('%s', fields);
END;
$$ LANGUAGE plpgsql;