CREATE OR REPLACE FUNCTION _debug_agg_json(netobj TEXT, fields TEXT[])
RETURNS TABLE(uid JSON) AS $$
DECLARE
    _field_placeholders TEXT[];
    tablename TEXT;
    f TEXT;
BEGIN
    tablename := FORMAT('%s', netobj);
    FOR f IN (SELECT UNNEST(fields)) LOOP
	_field_placeholders := array_append(_field_placeholders, FORMAT('%I', f));
    END LOOP;
    
    RAISE NOTICE '%', FORMAT('SELECT %s FROM %I', (SELECT array_to_string(_field_placeholders, ',')), tablename);
    RETURN QUERY
    SELECT array_to_json(array_agg(fa)) FROM temp;
END;
$$ LANGUAGE plpgsql;