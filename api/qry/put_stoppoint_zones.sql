WITH odpairs AS (
    SELECT
        ozoneno,
        dzoneno,
        pathindex
    FROM putpathlegs
    WHERE
        scen = '2015'
    AND tod = 'AM'
    AND fromstoppointno = ANY(ARRAY[101927]::INTEGER[])
    GROUP BY ozoneno, dzoneno, pathindex
    ORDER BY ozoneno, dzoneno
),
ppl AS (
    SELECT ppl.* FROM putpathlegs ppl
    INNER JOIN odpairs odp
    ON ppl.ozoneno = odp.ozoneno
    AND ppl.dzoneno = odp.dzoneno
    AND ppl.pathindex = odp.pathindex
),
_t AS (
    SELECT
        ozoneno
        ,dzoneno
        ,pathindex
        ,odtrips
        -- ,array_agg(array[fromstoppointno, tostoppointno])
    FROM ppl
    GROUP BY ozoneno, dzoneno, pathindex, odtrips
)
SELECT * FROM _t
ORDER BY odtrips DESC



SELECT ppl.ozoneno, ppl.dzoneno, ppl.pathindex, ppl.odtrips
FROM (SELECT * FROM tim_put_stoppoint_od(101927, '2015', 'AM')) AS odpi
LEFT JOIN putpathlegs ppl
    ON ppl.ozoneno = odpi.ozoneno
    AND ppl.dzoneno = odpi.dzoneno
    AND ppl.pathindex = odpi.pathindex