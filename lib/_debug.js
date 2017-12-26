var lastFeatures = {},
    NetworkObjects = {};

const MAPBOXGL_VISUM = {
    "wktloc": "circle",
    "wktpoly": "line",
    "wktsurface": "fill"
};
const VISUM_POSTGIS = {
    "wktloc": "gpt",
    "wktpoly": "gln",
    "wktsurface": "gpg"
}
const PAINT_DEFAULTS = {
    "wktloc": {
        "circle-color": "#f00",
        "circle-radius": 2,
    },
    "wktpoly": {
        "line-color": "#0f0",
        "line-width": 2,
    },
    "wktsurface": {
        "fill-color": "#ccc",
        "fill-opacity": 0.5,
        "fill-outline-color": "#fff"
    }
}

function MaxValGeoJSON(geojson, property) {
    var maxval = 0;
    for (i in geojson.features) {
        var f = geojson.features[i];
        if (f.properties[property] > maxval) {
            maxval = f.properties.totalval;
        }
    }
    return maxval;
}

function AddSourceGeoJSON(json, param) {
    map.addSource(param.sourceID, {
        type: "geojson",
        data: json
    });
}
function AddLayerGeoJSON(param, stops) {
    map.addLayer({
        id: param.layerID,
        type: param.geomType,
        source: param.sourceID,
        layout: "layout" in param ? param.layout : {},
        paint: "paint" in param ? param.paint : ("paintFn" in param ? param.paintFn(stops) : {})
    });
    if ("eventstyles" in param) {
        for (evt in param.eventstyles) {
            _addEventStyle(evt, param);
        }
    }
}
function _addEventStyle(evt, param) {
    var _param = param.eventstyles[evt];
    var _evtLayerID = param.layerID + "_" + evt;
    map.addLayer({
        id: _evtLayerID,
        type: param.geomType,
        source: param.sourceID,
        layout: "layout" in _param ? _param.layout : {},
        paint: "paint" in _param ? _param.paint : ("paintFn" in _param ? _param.paintFn(stops) : {}),
        filter: ["==", _param.property, ""]
    });
    map.on(evt, param.layerID, function (e) {
        var features = e.features;
        for (i in features) {
            if (features[i].layer.id === param.layerID) {
                map.setFilter(_evtLayerID, ["==", _param.property, features[i].properties[_param.property]]);
            }
        };
    });
}
function GetGeoJSON(URL, param) {
    $.getJSON(URL, function(json, success) {
        if (!success) {
            return;
        }
        AddSourceGeoJSON(json, param);
        AddLayerGeoJSON(param, "_stepFn" in param ? param._stepFn(json) : null);
    });
}

function GetSchema(callback) {
    $.getJSON("api/schema.php", function(json, success) {
        for (var i in json) {
            // Vorsicht! A proper meta table is required
            var tbl = json[i],
                c = tbl.t.split("_"),
                ttype = c[0],
                netobj = c[1];
            var fields = {};
            switch (ttype) {
                case "net":
                case "dat":
                case "geom":
                    if (!(netobj in NetworkObjects)) {
                        NetworkObjects[netobj] = {
                            net: {avail: false, fields: {}},
                            dat: {avail: false, fields: {}},
                            geom: {avail: false, fields: {}, gfields: {}, selected: ""},
                        };
                    }
                    NetworkObjects[netobj][ttype].avail = true;
                    NetworkObjects[netobj][ttype].fields = tbl.fs;
                    break;
                case "mtx":
                    if (!netobj in NetworkObjects) {
                        NetworkObjects[netobj] = {
                        };
                    }
                    break;
                default:
                    break;
            }
        }
        for (var netobj in NetworkObjects) {
            if (NetworkObjects[netobj].geom.avail) {
                NetworkObjects[netobj].geom.gfields = NetworkObjects[netobj].geom.fields.filter(f => f.startsWith("wkt"));
                NetworkObjects[netobj].geom.selected = NetworkObjects[netobj].geom.gfields[0];
            }
        }
        return callback();
    });
}

var deberg;
function PopulateUI() {
    for (var netobj in NetworkObjects) {
        var label = netobj;
        label += (NetworkObjects[netobj].net.avail) ? " N" : "";
        label += (NetworkObjects[netobj].dat.avail) ? " D" : "";
        label += (NetworkObjects[netobj].geom.avail) ? " G" : "";
        $("#datalayerslist").append(
            '<li class="ui-state-default"><span class="ui-icon ui-icon-arrowthick-2-n-s"></span><input type="checkbox" name="' + netobj + '">' + label + '</li>'
        );
        $('input[type=checkbox][name=' + netobj + ']').on('change', function() {
            var netobj = $(this)[0].name;
            if (NetworkObjects[netobj].geom.avail) {
                var f = NetworkObjects[netobj].geom.selected
                GetGeoJSON(
                    "api/" + netobj + ".php?t=" + VISUM_POSTGIS[f],
                    {
                        sourceID: "_" + netobj,
                        layerID: netobj,
                        geomType: MAPBOXGL_VISUM[f],
                        paint: PAINT_DEFAULTS[f]
                    }
                );
            } else {
                console.log(netobj, "has no geometry");
            }
        });
        
    }
}

/*
// Basic Geometry
// Point features
GetGeoJSON(
    "http://mario.dvrpc.org/dvrpc-tim-viewer/api/stops.php?t=gpt",
    {
        sourceID: "_stops",
        layerID: "stops",
        geomType: "circle",
        paint: {
            "circle-color": "#f00",
            "circle-radius": 5
        }
    }
);
// Line features
GetGeoJSON(
    "http://mario.dvrpc.org/dvrpc-tim-viewer/api/screenlines.php?t=gln",
    {
        sourceID: "_screenlines",
        layerID: "screenlines",
        geomType: "line",
        paint: {
            "line-color": "#0f0",
            "line-width": 2
        }
    }
);
*/

/*
// Polygon features
GetGeoJSON(
    "api/zones.php?t=gpg",
    {
        sourceID: "_zones",
        layerID: "zones",
        geomType: "fill",
        paint: {
            "fill-color": "#ccc",
            "fill-opacity": 0.5,
            "fill-outline-color": "#fff"
        },
        eventstyles: {
            click: {
                property: "no",
                paint: {
                    "fill-color": "#999",
                    "fill-opacity": 0.5,
                    "fill-outline-color": "#000"
                }
            },
        }
    }
);
*/

/*
// Advanced Geometry
// Weighted Lines
GetGeoJSON(
    "api/desirelines.php?t=vddl&m=2000&ozn=1&oz0=106&dzn=-1",
    {
        sourceID: "_vddl_1",
        layerID: "vddl_1",
        geomType: "line",
        _stepFn: function(json) {
            var steps = 40,
                width_multiplier = 3;
            var stops = [];
            var maxval = MaxValGeoJSON(json, "totalval"),
                step = maxval / steps;
            for (i = 0; i < maxval; i += step) {
                stops.push([i, width_multiplier*i/step]);
            }
            return stops;
        },
        paintFn: function(stops) {
            return {
                "line-color": "#888",
                "line-width": {
                    property: "totalval",
                    type: 'interval',
                    stops: stops
                }
            };
        },
        layout: {
            "line-join": "round",
            "line-cap": "round"
        }
    }
);
*/

$(function() {
    $("#datalayerslist").sortable();
    $("#datalayerslist").disableSelection();
    GetSchema(PopulateUI);
});