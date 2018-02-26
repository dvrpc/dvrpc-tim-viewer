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

var zone_temporal = [];
var activeAjaxConnections = 0;

$(document).ready(function(){
    $.ajax({
        type:'GET',
        url:'http://wololo.co/dvrpc-tim-viewer/api/zones.php?t=g&g=g',
        dataType:'JSON',
        data:{
        },
        beforeSend: function(){
        	activeAjaxConnections++;
        },
        success: function(data){
        	console.log(data);
        	activeAjaxConnections--;

            map.addSource("zones", {
		        type: "geojson",
		        data: data
		    });
            map.addSource('hover', {
		        type: 'geojson',
		        data: data
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
		        },
		        "filter": ['==', 'no', ""]
		    }, 'interstate-motorway_shields');
		    
		    //
			map.addLayer({
		        "id": "select-zone-fill",
		        "type": "fill",
		        "source": "hover",
		        'paint': {
		            "fill-opacity": 0.4,
		            'fill-color': '#f0ad4e',
		        },
		        "filter": ['==', 'no', ""]
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

		    // When the user moves their mouse over the layer, we'll update the filter in
		    // the hover layer to only show the matching feature, thus making a hover effect.
		    map.on("mousemove", "zone-fills-grid", function(e) {
		        map.setFilter("zone-fills", ["==", "no", e.features[0].properties['no']]);;
		    });

		    // Reset the state-fills-hover layer's filter when the mouse leaves the layer.
		    map.on("mouseleave", "zone-fills-grid", function() {
		        map.setFilter("zone-fills", ["==", "no", ""]);
		    });

			map.on('click', 'zone-fills', function (e) {
		        selectZone(e.features[0].properties.no);
		        map.setFilter("select-zone-fill", ["==", "no", e.features[0].properties.no]);
		    });

		    if (0 === activeAjaxConnections){
		    	setTimeout(function(){
				  	$('.sk-cube-grid').hide();
				}, 1250);
		    }
		    
        },
        error:function(XMLHttpRequest,textStatus,errorThrown){
            console.log("Error: unable to retrieve zone geometry")
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
        setTimeout(function(){
		  	$('.sk-cube-grid').hide();
		  	$('#map').removeClass('netouchepas');
		}, 1250);
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

function localDataCleaner(data) {
	var newData = {};
	
	for (i in data) {
		var _key = data[i].key.no;
		var _value = [];
		for (p in data[i].data) {
			_value[data[i].data[p].tod] = data[i].data[p];
		}
		
		newData[_key] = _value
	}
	
	return newData;
}

function selectZone(no) {
	select_zone = no;
	
	//build query
	var payload = JSON.stringify({
		    "netobj": "zone",
		    "keys": {"no": no},
		    "netfields": ["name", "population","total_employment","households","vehpp","area_type","autos"],
		    "datfields": {
		        "fields": ["otraffic_car", "dtraffic_car"],
		        "tod": ["AM"]
		    }
	    });
	var results = $.post('http://wololo.co/dvrpc-tim-viewer/api/zones.php', payload)
		.done(function(data){
			//success motherfucker, now do shit
			populateZoneProfile(data)
		});	

}

var zonenameDIV = $('#dat-zone-name');
var populationDIV = $('#dat-zone-population');
var householdsDIV = $('#dat-zone-households');
var employmentDIV = $('#dat-zone-employment');
var otherdataDIV = $('#data-dump');

function localHundredsFormat(num) {
	return num.toLocaleString(undefined, {maximumFractionDigits: 0});
}

function populateZoneProfile(zone) {
	var attData = zone.netpayload;

	zonenameDIV.html(zone.keys.no);

	employmentDIV.html(localHundredsFormat(attData.total_employment));
	populationDIV.html(localHundredsFormat(attData.population));
	householdsDIV.html(localHundredsFormat(attData.households));
}

//////////////////////////////////////////////
///// 
/////   desire lines
/////
///////////////////////

// desire line default
var trip_type = '2000';  			//default to car
var trip_direction = 'outbound';  	//default to outbound
var select_zone = ''; 

function getDesireLines(request) {
	$('.sk-cube-grid').show();
	$('#map').addClass('netouchepas');

	try {
     	map.removeLayer('vddl_1');
		map.removeSource('_vddl_1');
    }
    catch(err) {
	//        alert("Error!");
    }

	GetGeoJSON(
	    "http://wololo.co/dvrpc-tim-viewer/api/desirelines.php?"+request,
	    {
	        sourceID: "_vddl_1",
	        layerID: "vddl_1",
	        geomType: "line",
	        _stepFn: function(json) {
	            var steps = 30,
	                width_multiplier = 2.2;
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
	                "line-color": "#f4b387",
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

// event handlers

$('input[name="trip-type"').on('change', function(){ 
	trip_type = $(this).val();
});

$('input[name="trip-dir"').on('change', function(){ 
	trip_direction = $(this).val();
});

$('#desire-line-map').on('click', function(){
	var _req = "t=vddl&m="+trip_type+"&";
	
	if(trip_direction === 'outbound') {
		_req += "ozn=1&oz0="+ select_zone +"&dzn=-1";
	} else {
		_req += "ozn=-1&dzn=1&dz0="+ select_zone;
	}

	_req += "&todn=1&tod0=MD";

	getDesireLines(_req);
	
});

// declare some d3 chart bullshit
