mapboxgl.accessToken = mbconfig.token;

var map = new mapboxgl.Map({
  container: 'map',
  center: [-75.14, 39.95],
  zoom: 12,
  style: 'lib/map_styles/highway.json',
  hash: 'true',

});

// navigation control
var nav = new mapboxgl.NavigationControl();
map.addControl(nav, 'top-left');



$(document).ready(function(){
    $.ajax({
        type:'GET',
        url:'http://mario.dvrpc.org/dvrpc-tim-viewer/api/zones.php?t=g&g=g',
        dataType:'JSON',
        data:{
        },
        success:function(data){
            map.addSource("zones", {
		        type: "geojson",
		        data: data
		    });
            map.addSource('hover', {
		        type: 'geojson',
		        data: {
		            type: 'FeatureCollection',
		            features: []
		        }
		    });

		    // zone fill on hover
		    map.addLayer({
		        "id": "zone-fills-grid",
		        "type": "fill",
		        "source": "zones",
		        'paint': {
		            "fill-opacity": 0,
		            'fill-color': '#fff',
		        },
		        'filter': 
		                  [
		            "!=",
		            "no",
		            ""
		        ]
		    }, 'interstate-motorway_shields');

		    // zone fill on hover
		    map.addLayer({
		        "id": "zone-fills",
		        "type": "fill",
		        "source": "hover",
		        'paint': {
		            "fill-opacity": 0.4,
		            'fill-color': '#396AB2',
		        }
		    }, 'interstate-motorway_shields');

		    // base zone outline
		    map.addLayer({
		        "id": "zone-outline",
		        "type": "line",
		        "source": "zones",
		        'paint': {
		            "line-opacity": 0.4,
		            'line-color': '#312867',
		            'line-width': 2
		        }
		    }, 'interstate-motorway_shields');

		    // zone outline on hover
		    map.addLayer({
		        "id": "zone-outline-hover",
		        "type": "line",
		        "source": "zones",
		        'paint': {
		            "line-opacity": 1,
		            'line-color': '#312867',
		            'line-width': 3
		        },
		        'filter': 
		                  [
		            "==",
		            "no",
		            ""
		        ]
		    }, 'interstate-motorway_shields');

		    var hoveredFeature;
	        
	        // When the user moves their mouse over the layer, we'll update the filter in
		    // the hover layer to only show the matching feature, thus making a hover effect.
		    map.on("mousemove", "zone-fills-grid", function(e) {
		      if (e.features.length) {
		          var feature = e.features[0];
		          if (hoveredFeature !== feature.properties.no) {
		              hoveredFeature = feature.properties.no;
		              var sourceFeatures = map.querySourceFeatures("zones", {
		                  sourceLayer: "zone-fills",
		                  filter: ["==", "no", hoveredFeature]
		              });

		              console.log(sourceFeatures);
		              // join them together
		              if (sourceFeatures.length > 1) {
		                  feature = sourceFeatures[0];
		                  for (var i = 1; i < sourceFeatures.length; i++) {
		                      feature = turf.union(feature, sourceFeatures[i]);
		                  }
		              }

		              map.getSource('hover').setData(feature);
		          } // else same feature already hovered
		      } else {
		          clearHover();
		      }
		    });

		    // Reset the state-fills-hover layer's filter when the mouse leaves the layer.
		    map.on("mouseleave", "zone-fills-grid", clearHover);
		    
		    function clearHover() {
		        map.getCanvasContainer().style.cursor = null;
		        map.getSource('hover').setData({type: 'FeatureCollection', features: []});
		        hoveredFeature = null;
		    }

			map.on('click', 'zone-fills', function (e) {
		        getDesireLines(e.features[0].properties.no);
		    });
		    
        },
        error:function(XMLHttpRequest,textStatus,errorThrown){
            alert("error");
        }

    });
});

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

function GetGeoJSON(URL, param) {
    $.getJSON(URL, function(json, success) {
        if (!success) {
            return;
        }
        AddSourceGeoJSON(json, param);
        AddLayerGeoJSON(param, "_stepFn" in param ? param._stepFn(json) : null);
    });
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

function getDesireLines(no) {

	try {
     	map.removeLayer('vddl_1');
		map.removeSource('_vddl_1');
    }
    catch(err) {
//        alert("Error!");
    }

	GetGeoJSON(
	    "http://mario.dvrpc.org/dvrpc-tim-viewer/api/desirelines.php?t=vddl&m=2000&ozn=1&oz0="+ no +"&dzn=-1",
	    {
	        sourceID: "_vddl_1",
	        layerID: "vddl_1",
	        geomType: "line",
	        _stepFn: function(json) {
	            var steps = 30,
	                width_multiplier = 2;
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
}