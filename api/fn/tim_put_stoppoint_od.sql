DROP FUNCTION IF EXISTS tim_put_stoppoint_od(INTEGER[], TEXT, TEXT);
DROP FUNCTION IF EXISTS tim_put_stoppoint_od(INTEGER, TEXT, TEXT);

CREATE OR REPLACE FUNCTION tim_put_stoppoint_od(stoppoints INTEGER[], scenario TEXT, timeofday TEXT)
RETURNS TABLE (
    ozoneno INTEGER,
    dzoneno INTEGER,
    pathindex INTEGER
) AS $$
BEGIN
    RETURN QUERY
        SELECT
            ppl.ozoneno,
            ppl.dzoneno,
            ppl.pathindex
        FROM putpathlegs ppl
        WHERE
            ppl.scen = scenario
        AND ppl.tod = timeofday
        -- (to|from)stoppointno are offset from each other by one with a (trailing|leading) null
        AND ppl.fromstoppointno = ANY(stoppoints)
        GROUP BY ppl.ozoneno, ppl.dzoneno, ppl.pathindex
        ORDER BY ppl.ozoneno, ppl.dzoneno, ppl.pathindex;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION tim_put_stoppoint_od(stoppoint INTEGER, scenario TEXT, timeofday TEXT)
RETURNS TABLE (
    ozoneno INTEGER,
    dzoneno INTEGER,
    pathindex INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM tim_put_stoppoint_od(ARRAY[stoppoint]::INTEGER[], scenario, timeofday);
END;
$$ LANGUAGE plpgsql;