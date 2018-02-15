WITH
ttype_netobjs AS (
SELECT
	netobj,
	'net_' || netobj net_table,
	'dat_' || netobj dat_table,
	'geom_' || netobj geom_table,
	array_to_json(array_agg((SELECT r FROM (SELECT field, dtype) r))) keys
FROM tim_netobj_keys
GROUP BY netobj
),
meta_netobjs AS (
SELECT
	table_name,
	array_to_json(array_agg((SELECT r FROM (SELECT column_name f, udt_name d) r))) fields
FROM meta
GROUP BY table_name
)
SELECT
	tno.netobj,
	tno.keys,
	-- CASE WHEN tno.net_table IN (SELECT table_name FROM meta_netobjs) THEN TRUE ELSE FALSE END net_avail,
	-- CASE WHEN tno.dat_table IN (SELECT table_name FROM meta_netobjs) THEN TRUE ELSE FALSE END dat_avail,
	-- CASE WHEN tno.geom_table IN (SELECT table_name FROM meta_netobjs) THEN TRUE ELSE FALSE END geom_avail,
	net_mno.fields net,
	dat_mno.fields dat,
	geom_mno.fields geom
FROM ttype_netobjs tno
LEFT JOIN meta_netobjs net_mno ON net_mno.table_name = tno.net_table
LEFT JOIN meta_netobjs dat_mno ON dat_mno.table_name = tno.dat_table
LEFT JOIN meta_netobjs geom_mno ON geom_mno.table_name = tno.geom_table
WHERE tno.net_table IN (SELECT table_name FROM meta_netobjs)
ORDER BY netobj
