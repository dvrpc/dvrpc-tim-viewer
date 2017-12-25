CREATE OR REPLACE FUNCTION tim_dat_listnetobjattrs(netobj TEXT)
RETURNS JSON AS $$
DECLARE
    retval JSON;
BEGIN
    EXECUTE('
    SELECT array_to_json(array_agg(column_name::text))
    FROM meta WHERE table_name = $1
    ') USING FORMAT('dat_%s', netobj) INTO retval;
    RETURN retval;
END;
$$ LANGUAGE plpgsql;