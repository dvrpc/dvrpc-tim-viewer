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

var steps = 40;
var width_multiplier = 2;

map.on('load', function() {
    getJSON("http://mario.dvrpc.org/dvrpc-tim-viewer/api/desirelines.php?t=vddl&m=2000&ozn=1&oz0=106&dzn=-1", function(success, json) {
        if (!success) {
            return;
        }
        var maxval = 0,
            stops = [];
        for (i in json.features) {
            var f = json.features[i];
            if (f.properties.totalval > maxval) {
                maxval = f.properties.totalval;
            }
        }
        var step = maxval / steps;
        for (i = 0; i < maxval; i += step) {
            stops.push([i, width_multiplier*i/step]);
        }
        map.addLayer({
            "id": "aa",
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
                "line-color": "#888",
                "line-width": {
                    property: 'totalval',
                    type: 'interval',
                    stops: stops
                }
            }
        });
    });
});