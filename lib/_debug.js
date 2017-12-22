var getJSON = function(url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'json';
    xhr.onload = function() {
      var status = xhr.status;
      if (status === 200) {
        callback(true, xhr.response);
      } else {
        callback(status, xhr.response);
      }
    };
    xhr.send();
};

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
}
function GetGeoJSON(URL, param) {
    getJSON(URL, function(success, json) {
        if (!success) {
            return;
        }
        AddSourceGeoJSON(json, param);
        AddLayerGeoJSON(param, "_stepFn" in param ? param._stepFn(json) : null);
    });
}

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
// Polygon features
GetGeoJSON(
    "http://mario.dvrpc.org/dvrpc-tim-viewer/api/zones.php?t=gpg",
    {
        sourceID: "_zones",
        layerID: "zones",
        geomType: "fill",
        paint: {
            "fill-color": "#ccc",
            "fill-opacity": 0.5,
            "fill-outline-color": "#fff"
        }
    }
);

// Advanced Geometry
// Weighted Lines
GetGeoJSON(
    "http://mario.dvrpc.org/dvrpc-tim-viewer/api/desirelines.php?t=vddl&m=2000&ozn=1&oz0=106&dzn=-1",
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