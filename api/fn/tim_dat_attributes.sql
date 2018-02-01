CREATE OR REPLACE FUNCTION tim_dat_attributes(netobj TEXT, fields TEXT[])
RETURNS JSON AS $$
DECLARE
    idfields TEXT[];
    foundfields TEXT[];
    trgt_tblname TEXT;
    retval JSON;
BEGIN
    trgt_tblname := FORMAT('net_%s', netobj);

    SELECT array_agg(meta_netobj.field::text) INTO idfields
    FROM meta_netobj
    WHERE meta_netobj.netobj = tim_dat_attributes.netobj;

    SELECT array_agg(meta.column_name::text) INTO foundfields
    FROM meta
    WHERE meta.table_name = trgt_tblname
    AND meta.column_name IN (SELECT UNNEST(fields));

    EXECUTE(FORMAT(
        '
        SELECT array_to_json(array_agg(row_to_json(t))) FROM (
            SELECT
            row_to_json((SELECT s FROM (SELECT %s) s)) AS key,
            json_agg((SELECT s FROM (SELECT %s) s)) AS data
            FROM %I _t
            GROUP BY %s
        ) t
        ',
        (SELECT array_to_string(idfields, ',')),
        (SELECT array_to_string(foundfields, ',')),
        trgt_tblname,
        (SELECT array_to_string(idfields, ','))
    )) INTO retval;

    RETURN retval;

END;
$$ LANGUAGE plpgsql;