-- {MTXNO} msec, xeon e5-2687w v4, nvme ssd
SELECT
    am.oindex, am.dindex,
    am.val am, md.val md,
    pm.val pm, nt.val nt
FROM mtx_{MTXNO}_am am
INNER JOIN mtx_{MTXNO}_md md
ON am.oindex = md.oindex AND am.dindex = md.dindex
INNER JOIN mtx_{MTXNO}_pm pm
ON am.oindex = pm.oindex AND am.dindex = pm.dindex
INNER JOIN mtx_{MTXNO}_nt nt
ON am.oindex = nt.oindex AND am.dindex = nt.dindex
WHERE am.oindex = {ZONENO}

UNION ALL

SELECT
    am.oindex, am.dindex,
    am.val am, md.val md,
    pm.val pm, nt.val nt
FROM mtx_{MTXNO}_am am
INNER JOIN mtx_{MTXNO}_md md
ON am.oindex = md.oindex AND am.dindex = md.dindex
INNER JOIN mtx_{MTXNO}_pm pm
ON am.oindex = pm.oindex AND am.dindex = pm.dindex
INNER JOIN mtx_{MTXNO}_nt nt
ON am.oindex = nt.oindex AND am.dindex = nt.dindex
WHERE am.dindex = {ZONENO}