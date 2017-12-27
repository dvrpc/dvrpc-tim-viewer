CREATE OR REPLACE FUNCTION tim_dat_attributes(netobj TEXT, fields TEXT[])
RETURNS JSON AS $$
DECLARE
    idfields TEXT[];
    foundfields TEXT[];
    id_tblname TEXT;
    dat_tblname TEXT;
    retval JSON;
BEGIN
    id_tblname := FORMAT('net_%s', netobj);
    dat_tblname := FORMAT('dat_%s', netobj);

    SELECT array_agg(meta.column_name::text) INTO idfields
    FROM meta
    WHERE meta.table_name = id_tblname;

    SELECT array_agg(meta.column_name::text) INTO foundfields
    FROM meta
    WHERE meta.table_name = dat_tblname
    AND meta.column_name IN (SELECT UNNEST(fields));

    EXECUTE(FORMAT(
        '
        SELECT array_to_json(array_agg(row_to_json(t))) FROM (
            SELECT
            row_to_json((SELECT s FROM (SELECT %s) s)) AS key,
            row_to_json((SELECT s FROM (SELECT %s) s)) AS data
            FROM %I _t
            GROUP BY %s
        ) t
        ',
        (SELECT array_to_string(idfields, ',')),
        (SELECT array_to_string(foundfields, ',')),
        dat_tblname,
        (SELECT array_to_string(idfields, ','))
    )) INTO retval;

    RETURN retval;


END;
$$ LANGUAGE plpgsql;