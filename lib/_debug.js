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

function GetWeightedLineGeoJSON(URL, param) {
    getJSON(URL, function(success, json) {
        if (!success) {
            return;
        }
        var stops = [];
        var maxval = MaxValGeoJSON(json, param.property),
            step = maxval / param.steps;
        for (i = 0; i < maxval; i += step) {
            stops.push([i, param.width_multiplier*i/step]);
        }
        map.addLayer({
            "id": param.id,
            "type": "line",
            "source": {
                "type": "geojson",
                "data": json
            },
            "layout": {
                "line-join": "round",
                "line-cap": "round"
            },
            "paint": {
                "line-color": param.linecolor,
                "line-width": {
                    property: param.property,
                    type: 'interval',
                    stops: stops
                }
            }
        });
    });
}

function GetLineGeoJSON(URL, param) {
    getJSON(URL, function(success, json) {
        if (!success) {
            return;
        }
        var stops = [];
        var maxval = MaxValGeoJSON(json, param.property),
            step = maxval / param.steps;
        for (i = 0; i < maxval; i += step) {
            stops.push([i, param.width_multiplier*i/step]);
        }
        map.addLayer({
            "id": param.id,
            "type": "line",
            "source": {
                "type": "geojson",
                "data": json
            },
            "layout": {
                "line-join": "round",
                "line-cap": "round"
            },
            "paint": {
                "line-color": param.linecolor,
                "line-width": param.linewidth
            }
        });
    });
}

GetWeightedLineGeoJSON(
    "http://mario.dvrpc.org/dvrpc-tim-viewer/api/desirelines.php?t=vddl&m=2000&ozn=1&oz0=106&dzn=-1",
    {
        id: "vddl-1",
        property: "totalval",
        steps: 40,
        width_multiplier: 2,
        linecolor: "#888"
    }
)
GetLineGeoJSON(
    "http://mario.dvrpc.org/dvrpc-tim-viewer/api/screenlines.php?t=gln",
    {
        id: "screenlines",
        linecolor: "#0f0",
        linewidth: 2
    }
)
GetLineGeoJSON(
    "http://mario.dvrpc.org/dvrpc-tim-viewer/api/lineroutes.php?t=gln",
    {
        id: "lineroutes",
        linecolor: "#00f",
        linewidth: 2
    }
)
// map.on('load', function() {
    // getJSON(, function(success, json) {
        // if (!success) {
            // return;
        // }
        // var maxval = 0,
            // stops = [];
        // for (i in json.features) {
            // var f = json.features[i];
            // if (f.properties.totalval > maxval) {
                // maxval = f.properties.totalval;
            // }
        // }
        // var step = maxval / steps;
        // for (i = 0; i < maxval; i += step) {
            // stops.push([i, width_multiplier*i/step]);
        // }
        // map.addLayer({
            // "id": "aa",
            // "type": "line",
            // "source": {
                // "type": "geojson",
                // "data": json
            // },
            // "layout": {
                // "line-join": "round",
                // "line-cap": "round"
            // },
            // "paint": {
                // "line-color": "#888",
                // "line-width": {
                    // property: 'totalval',
                    // type: 'interval',
                    // stops: stops
                // }
            // }
        // });
    // });
// });
