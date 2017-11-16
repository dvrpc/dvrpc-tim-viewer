-- 210 msec, xeon e5-2687w v4, nvme ssd
SELECT
    am.oindex, am.dindex,
    am.val am, md.val md,
    pm.val pm, nt.val nt
FROM mtx_210_am am
INNER JOIN mtx_210_md md
ON am.oindex = md.oindex AND am.dindex = md.dindex
INNER JOIN mtx_210_pm pm
ON am.oindex = pm.oindex AND am.dindex = pm.dindex
INNER JOIN mtx_210_nt nt
ON am.oindex = nt.oindex AND am.dindex = nt.dindex
WHERE am.oindex = 1

UNION ALL

SELECT
    am.oindex, am.dindex,
    am.val am, md.val md,
    pm.val pm, nt.val nt
FROM mtx_210_am am
INNER JOIN mtx_210_md md
ON am.oindex = md.oindex AND am.dindex = md.dindex
INNER JOIN mtx_210_pm pm
ON am.oindex = pm.oindex AND am.dindex = pm.dindex
INNER JOIN mtx_210_nt nt
ON am.oindex = nt.oindex AND am.dindex = nt.dindex
WHERE am.dindex = 1