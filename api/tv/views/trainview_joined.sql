CREATE OR REPLACE VIEW trainview_joined AS
SELECT
    trainview.id,
    trainview.tstz,
    lines.line,
    services.service,
    trainnos.trainno,
    consists.consist,
    ostops.stop AS origstop,
    dstops.stop AS deststop,
    nstops.stop AS nextstop,
    tracks.track,
    changetracks.track AS trackchange,
    trainview.heading,
    trainview.late,
    trainview.lat,
    trainview.lon
FROM trainview
LEFT JOIN lines ON trainview.lineid = lines.id
LEFT JOIN services ON trainview.serviceid = services.id
LEFT JOIN trainnos ON trainview.trainnoid = trainnos.id
LEFT JOIN consists ON trainview.consistid = consists.id
LEFT JOIN stops ostops ON trainview.originid = ostops.id
LEFT JOIN stops dstops ON trainview.destid = dstops.id
LEFT JOIN stops nstops ON trainview.nextstopid = nstops.id
LEFT JOIN tracks ON trainview.trackid = tracks.id
LEFT JOIN tracks changetracks ON trainview.trackchangeid = changetracks.id;
