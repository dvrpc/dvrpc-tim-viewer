SELECT
    (rownum - 1)::INTEGER indexno,
    no
FROM (
    SELECT
        row_number() OVER (ORDER BY no NULLS LAST) rownum,
        no
    FROM tim23_zone
    ORDER BY no
) _q