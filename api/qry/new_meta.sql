WITH
ttype_netobjs AS (
    SELECT
        netobj,
        'net_' || netobj net_table,
        'dat_' || netobj dat_table,
        'geom_' || netobj geom_table,
        array_agg(field) keys
    FROM tim_netobj_keys
    GROUP BY netobj
),
meta_netobjs AS (
    SELECT
        table_name,
        array_agg(column_name::TEXT) fields
    FROM meta
    LEFT JOIN ttype_netobjs tno
    ON (
        tno.net_table = table_name
    OR  tno.dat_table = table_name
    OR  tno.geom_table = table_name
    )
    WHERE NOT (meta.column_name::TEXT = ANY(tno.keys))
    GROUP BY table_name
)
SELECT
    tno.netobj,
    tno.keys,
    net_mno.fields net,
    dat_mno.fields dat,
    geom_mno.fields geom
FROM ttype_netobjs tno
LEFT JOIN meta_netobjs net_mno ON net_mno.table_name = tno.net_table
LEFT JOIN meta_netobjs dat_mno ON dat_mno.table_name = tno.dat_table
LEFT JOIN meta_netobjs geom_mno ON geom_mno.table_name = tno.geom_table
WHERE tno.net_table IN (SELECT table_name FROM meta_netobjs)
ORDER BY netobj
