CREATE OR REPLACE VIEW transitview_joined AS 
SELECT
    transitview.id,
    transitview.tstz,
    lines.line,
    transitview.lat,
    transitview.lon,
    transitview.heading,
    transitview.label,
    transitview.trip,
    transitview.vehicleid,
    transitview.blockid,
    directions.direction,
    destinations.destination,
    transitview.offset_wut,
    transitview.offset_sec,
    transitview.late
FROM transitview
LEFT JOIN lines ON transitview.lineid = lines.id
LEFT JOIN directions ON transitview.directionid = directions.id
LEFT JOIN destinations ON transitview.destinationid = destinations.id;
