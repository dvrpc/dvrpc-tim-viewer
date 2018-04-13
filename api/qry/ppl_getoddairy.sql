-- SELECT * FROM putpathlegs LIMIT 10
WITH cws AS (
SELECT -- *,
	ozoneno,
	dzoneno,
	pathindex,
	pathlegindex,
	odtrips,
	ARRAY[fromstoppointno, tostoppointno] odstoppointnos,
	CASE WHEN linename IS NULL THEN 
		ARRAY[timeprofilekeystring, NULL]
	ELSE 
		ARRAY[linename, tsyscode]
	END descrip
FROM putpathlegs
WHERE
	ozoneno = 10426
AND	(fromstoppointno IS NOT NULL AND tostoppointno IS NOT NULL)
AND	TOD = 'AM'
AND	scen = '2015'

ORDER BY ozoneno, dzoneno, pathindex, pathlegindex
),
acws AS (
SELECT
	ozoneno, dzoneno, pathindex,
	AVG(odtrips) odtrips,
	array_agg(odstoppointnos) odstoppointnos,
	array_agg(descrip) descripts
FROM cws
GROUP BY ozoneno, dzoneno, pathindex
)
SELECT json_agg(row_to_json(acws))
FROM acws