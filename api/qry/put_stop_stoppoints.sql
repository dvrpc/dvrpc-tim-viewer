WITH stopburger AS (
SELECT sps.no spno, sps.stopareano sano, sas.sno FROM net_stoppoint sps
LEFT JOIN (SELECT no sano, stopno sno FROM net_stoparea) sas
ON sps.stopareano = sas.sano
),
sno_spnos AS (
SELECT
    array_agg(spno) spnos,
    array_agg(sano) sanos,
    sno
FROM stopburger
GROUP BY sno
)
SELECT s.no, s.code, s.name, sno_spnos.spnos FROM net_stop s INNER JOIN sno_spnos ON s.no = sno_spnos.sno
ORDER BY s.no