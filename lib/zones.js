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

// [
// "case", 
// ['==', ['get', "user_class_id"], 1], "#00ff00", 
// ['==', ['get', "user_class_id"], 2], "#0000ff",
// '#ff0000'
// ],

map.on('load', function(){
	
	map.addSource("zones", {
		type: "vector",
		url: "https://tiles.dvrpc.org/data/dvrpc-tim-zones.json"
	});

	map.addSource("hover", {
		type: "vector",
		url: "https://tiles.dvrpc.org/data/dvrpc-tim-zones.json"
	});

	// zone fill on hover
	map.addLayer({
		"id": "zone-fills-grid",
		"type": "fill",
		"source": "zones",
		"source-layer": "tim-zones",
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
		"source-layer": "tim-zones",
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
		"source-layer": "tim-zones",
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
		"source-layer": "tim-zones",
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
		"source-layer": "tim-zones",
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
	

})

function Kalp() {
	var popdensityhack = $.getJSON('https://wololo.co/dvrpc-tim-viewer/api/zones.php?t=a&fn=2&f0=taz_area&f1=population', function(json, success) {
		if (!success) {
			return;
		}
		const matchExpression = ['case'];
		var maxvalue = 0;
		json.forEach((zone, index) => {
			var popden = zone.data[0].population / zone.data[0].taz_area;
			if (popden > maxvalue) {
				maxvalue = popden;
			}
		});
		// map.setPaintProperty("zone-fills-grid", "fill-color", ["case", ["==", ["get", "no"], 1], "rgb(255,0,0)", "rgb(0,255,0)"])
		json.forEach((zone, index) => {
			var popden = zone.data[0].population / zone.data[0].taz_area;
			var color_index = 0;
			if (zone.data[0].taz_area > 0) {
				color_index = Math.ceil(10 * Math.pow(popden, 0.25) / Math.pow(maxvalue, 0.25));
			}
			matchExpression.push(['==', ['get', 'no'], zone.key.no], color_ramp[color_index]);
		});
		matchExpression.push('rgba(0, 255, 255, 255)');
		map.setPaintProperty("zone-fills-grid", 'fill-color', matchExpression);
		map.setPaintProperty("zone-fills-grid", 'fill-opacity', 0.5);
	});
}
function _getAPI(url, attr) {
    var data = $.getJSON(url, function (json, success) {
        if (!success) {
            return;
        }
        const matchExpression = ['case'];
        var maxValue = 0;
        json.forEach((zone, index) => {
            var value = zone.data[0][attr];
            if (value > maxValue) {
                maxValue = value;
            }
        });
        json.forEach((zone, index) => {
            var value = zone.data[0][attr];
            var color_index = 0;
            if (value != null) {
                color_index = Math.ceil(10 * Math.pow(value, 0.25) / Math.pow(maxValue, 0.25));
            }
            matchExpression.push(['==', ['get', 'no'], zone.key.no], color_ramp[color_index]);
        });
        matchExpression.push('rgba(0, 255, 255, 255)');
        map.setPaintProperty("zone-fills-grid", 'fill-color', matchExpression);
        map.setPaintProperty("zone-fills-grid", 'fill-opacity', 0.5);
    });
}
function getTransitAccess() {
    return _getAPI('https://wololo.co/dvrpc-tim-viewer/api/zones.php?t=a&fn=1&f0=pct_qtrmi_transit', 'pct_qtrmi_transit');
}
function getNearbyEmp() {
    return _getAPI('https://wololo.co/dvrpc-tim-viewer/api/zones.php?t=a&fn=1&f0=emp_1mi', 'emp_1mi');
}
function Sylph() {
	map.setPaintProperty("zone-fills-grid", 'fill-color', '#fff');
	map.setPaintProperty("zone-fills-grid", 'fill-opacity', 0.0);
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
	console.log(no)
	//build query
	var payload = JSON.stringify({
		    "netobj": "zone",
		    "keys": {"no": no},
			"netfields": ["name", "population","total_employment","households","area_type","autos","ag_mining","arts_rec_food" ,"construction","eds_meds","fire","information","manufacturing","other_services","prof_services","public_admin","retail_trade","transport_wh_util","wholesale_trade",
				"empres",
				"k_12",
				"univ",
				"stu_colleg",
				"stu_school",
				"taz_area",
                "pct_qtrmi_transit",
                "emp_1mi"
			],
		    "datfields": {
		        "fields": ["otraffic_car", "dtraffic_car"],
		        "tod": ["AM"]
		    }
	    });
	var results = $.post('https://wololo.co/dvrpc-tim-viewer/api/zones.php', payload)
		.done(function(data){
			//success motherfucker, now do shit
			console.log(data);
			populateZoneProfile(data)
		});	

}

//industry lookup for better names
var industryLookup = {
	"ag_mining" : { name: "Agriculture, Forestry, Fishing and Hunting; Mining, Quarrying, and Oil and Gas Extraction", short: "Agriculture and Mining"},
	"arts_rec_food" : { name: "Accommodation and Food Services; Arts, Entertainment, and Recreation", short: "Arts, Recreation, and Food Services"}, 
	"construction" : { name: "Construction", short: "Construction"},
	"eds_meds" : { name: "Educational Services; Health Care and Social Assistance", short: "Eds and Meds"},
	"fire" : { name: "Finance and Insurance; Real Estate and Rental and Leasing", short: "FIRE"},
	"information" : { name: "Information", short: "Information"},
	"manufacturing" : { name: "Manufacturing", short: "Manufacturing"},
	"other_services" : { name: "Other Services (except Public Administration)", short: "Other Services (except Public Administration)"},
	"prof_services" : { name: "Professional, Scientific, and Technical Services; Administrative and Support and Waste Management and Remediation Services", short: "Professional Services"},
	"public_admin" : { name: "Public Administration", short: "Public Administration"},
	"retail_trade" : { name: "Retail Trade", short: "Retail Trade"},
	"transport_wh_util" : { name: "Transportation and Warehousing; Utilities", short: "Transportation, Warehouse, and Utilities"},
	"wholesale_trade" : { name: "Wholesale Trade", short: "Wholesale Trade"}
};

var zonenameDIV = $('#dat-zone-name');
var populationDIV = $('#dat-zone-population');
var popdensityDIV = $('#dat-zone-popdensity');
var householdsDIV = $('#dat-zone-households');
var empresDIV = $('#dat-zone-empres');
var employmentDIV = $('#dat-zone-employment');
var transitaccDIV = $('#dat-zone-transitaccess');
var nearbyempDIV = $('#dat-zone-nearbyemp');
var k12DIV = $('#dat-zone-k_12');
var univDIV = $('#dat-zone-univ');
var stu_collegeDIV = $('#dat-zone-stu_college');
var stu_schoolDIV = $('#dat-zone-stu_school');
var otherdataDIV = $('#data-dump');

function localHundredsFormat(num) {
	return num.toLocaleString(undefined, {maximumFractionDigits: 0});
}

function populateZoneProfile(zone) {
	deleteLines();
	var attData = zone.netpayload;

	zonenameDIV.html(zone.keys.no);

	employmentDIV.html(localHundredsFormat(attData.total_employment));
	populationDIV.html(localHundredsFormat(attData.population));
	popdensityDIV.html(localHundredsFormat(attData.population/ attData.taz_area));
	empresDIV.html(localHundredsFormat(attData.empres));
	householdsDIV.html(localHundredsFormat(attData.households));
	//education
	k12DIV.html(localHundredsFormat(attData.k_12));
	univDIV.html(localHundredsFormat(attData.univ));
	stu_collegeDIV.html(localHundredsFormat(attData.stu_colleg));
	stu_schoolDIV.html(localHundredsFormat(attData.stu_school));
    transitaccDIV.html((attData.pct_qtrmi_transit * 100).toFixed(1) + '%');
    nearbyempDIV.html(localHundredsFormat(attData.emp_1mi));

	renderEmploymentViz("#employment-graph", attData)
}

var treeData = function(data) {
	var readyData = [{content: "industries", parent: "", count: undefined}]; 
	// var readyData = []; 
	for ( var industry in industryLookup) {
		readyData.push({
			content: industryLookup[industry].short,
			parent: industry,
			count: data[industry],
			full: industryLookup[industry].name 
		});

		readyData.push({
			content: industry,
			parent: "industries",
			count: undefined,
			full: undefined
		});
	}

	return readyData;
}

// builder for the employment tree map
var vWidth = $('#zone-sidebar').width();
var vHeight = 250;

var color = d3.scaleOrdinal()
    .range(d3.schemeCategory20
        .map(function(c) { c = d3.rgb(c); c.opacity = 0.6; return c; }));
// Ignore the above
// White (0) -> Yellow -> Red
var color_ramp = [
	"rgb(255,255,255)",
	"rgb(253,250,204)",
	"rgb(252,246,154)",
	"rgb(251,242,104)",
	"rgb(250,238,54)",
	"rgb(249,234,4)",
	"rgb(246,199,7)",
	"rgb(243,164,11)",
	"rgb(241,130,14)",
	"rgb(238,95,18)",
	"rgb(236,61,22)",
]


var format = d3.format(",d");

//build a holder for chart
var temporary = d3.select("#employment-graph").append("svg")
	.attr("class", "temp")
	.attr("width", vWidth).attr("height", vHeight);
temporary.append("rect").attr("width", vWidth).attr("height", vHeight)
		.attr("fill", "#e7e7e7");
temporary.append("text")
	.text("Click zone to populate chart")
	.attr("fill", "#636c72").attr("x","50%").attr("y","50%").attr("alignment-baseline", "middle").attr("text-anchor", "middle");

function renderEmploymentViz(svg, data) {
	var treemap = d3.treemap()
	    .size([vWidth, vHeight])
	    .padding(0.6)
	    .round(true);

	var stratify = d3.stratify()
	  	.id(function(d) { return d.content; })
	  	.parentId(function(d) { return d.parent; });

	var vdata = treeData(data);
	var root = stratify(vdata);
	
	root.each(function(d) {
	    d.name = d.id;
	});

	var graph = d3.select(svg);

	//remove that holder shit
	graph.selectAll('.temp').data([]).exit().remove();

	function draw (root, data){
		root
	      .sum(function(d) { return d.count; })
	      .sort(function(a, b) { return b.height - a.height || b.count - a.count; });

		treemap(root);
	    

	    graph.selectAll('.node')
	      .data(root.leaves())
	      .enter().append("div")
	        .attr("class", "node")
	      .append("div")
        	.attr("class", "node-label");

        graph.selectAll('.node-label')
        	.data(root.leaves())
        	.enter();
	      
	    graph.selectAll('.node')
	        .attr("title", function(d) { return d.data.full + "\n" + format(d.value); })
	        .style("left", function(d) { return d.x0 + "px"; })
	        .style("top", function(d) { return d.y0 + "px"; })
	        .style("width", function(d) { return d.x1 - d.x0 + "px"; })
	        .style("height", function(d) { return d.y1 - d.y0 + "px"; })
	        .style("background", function(d) { return color(d.id); });

	    graph.selectAll('.node-label')
	        .text(function(d) { return d.id + "\n" + format(d.value); });

	}

	draw(root, vdata);
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
var trip_tod = 'AM'; 

var deleteLines = function() {
	try {
     	map.removeLayer('vddl_1');
		map.removeSource('_vddl_1');
	} catch (err) {
		console.log("Data layer doesnt exist yet");
	}
}
function getDesireLines(request) {
	$('.sk-cube-grid').show();
	$('#map').addClass('netouchepas');

	deleteLines();

	GetGeoJSON(
	    "https://wololo.co/dvrpc-tim-viewer/api/desirelines.php?"+request,
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

$('input[name="trip-tod"').on('change', function(){ 
	trip_tod = $(this).val();
});

$('#desire-line-map').on('click', function(){
	var _req = "t=ddl&m="+trip_type+"&";
	
	if(trip_direction === 'outbound') {
		_req += "ozn=1&oz0="+ select_zone +"&dzn=-1";
	} else {
		_req += "ozn=-1&dzn=1&dz0="+ select_zone;
	}

	_req += "&todn=1&tod0="+trip_tod;

	getDesireLines(_req);
	
});

$('.nav-link').on('click', function(e) {
	switch(e.currentTarget.hash) {
		case "#zone-popdensity":
			Kalp();
			break;
        case "#zone-transitaccess":
            getTransitAccess();
            break;
        case "#zone-nearbyemp":
            getNearbyEmp();
            break;
		default:
			Sylph();
	}
});

// declare some d3 chart bullshit
