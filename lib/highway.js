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




// define functional class colors
const _01_freeway = '#fdb462';
const _02_parkway = '#b3de69';
const _03_major_art = '#bc80bd';
const _04_minor_art = '#bebada';
const _05_major_coll = '#8dd3c7';
const _06_minor_coll = '#ccebc5';
const _07_local = '#fccde5';
const _08_ramp = '#fb8072';
const _09_other = '#d9d9d9';

const highway_layers = ['freeways', 'major_arterials', 'minor_arterials', 'major_collectors', 'minor_collectors', 'locals'];

const fc_legend = '<i class="fa fa-minus" style="color:'+_01_freeway+'"></i>&nbsp;&nbsp;Freeway<br/><i class="fa fa-minus" style="color:'+_02_parkway+'"></i>&nbsp;&nbsp;Parkway<br/><i class="fa fa-minus" style="color:'+_03_major_art+'"></i>&nbsp;&nbsp;Major Arterial<br/><i class="fa fa-minus" style="color:'+_04_minor_art+'"></i>&nbsp;&nbsp;Minor Arterial<br/><i class="fa fa-minus" style="color:'+_05_major_coll+'"></i>&nbsp;&nbsp;Major Collector<br/><i class="fa fa-minus" style="color:'+_06_minor_coll+'"></i>&nbsp;&nbsp;Minor Collector<br/><i class="fa fa-minus" style="color:'+_07_local+'"></i>&nbsp;&nbsp;Local<br/><i class="fa fa-minus" style="color:'+_08_ramp+'"></i>&nbsp;&nbsp;Ramp<br/>';

const tl_legend = '<i class="fa fa-minus" style="color:#fef0d9"></i>&nbsp;&nbsp;1 lane<br/><i class="fa fa-minus" style="color:#fdbb84"></i>&nbsp;&nbsp;2 lane<br/><i class="fa fa-minus" style="color:#fc8d59"></i>&nbsp;&nbsp;3 lane<br/><i class="fa fa-minus" style="color:#e34a33"></i>&nbsp;&nbsp;4+ lane<br/>';

var legend = document.getElementById('legend');

function clearHighwayStyle(){
	legend.innerHTML = "";
	map.setFilter('highways-fc-styled', ["in", "typeno", " "]);
	map.setFilter('locals-fc-styled', ["in", "typeno", " "]);
	map.setFilter('highways-lanes-styled', ["in", "typeno", " "]);
	map.setFilter('locals-lanes-styled', ["in", "typeno", " "]);
}


$('input[type=radio][name=hwy-render-state]').on('change', function() {
	if($(this).val() == 'hwy-no-style'){
		clearHighwayStyle();
	} else if($(this).val() == 'hwy-fc-style'){
		clearHighwayStyle()
    	legend.innerHTML = fc_legend;
    	map.setFilter('highways-fc-styled', ["!in", "typeno", "71","72","73","75","76","79"]);
    	map.setFilter('locals-fc-styled', ["in", "typeno", "71","72","73","75","76","79"]);
	} else if($(this).val() == 'hwy-tl-style'){
		clearHighwayStyle()
    	legend.innerHTML = tl_legend;
    	map.setFilter('highways-lanes-styled', ["!in", "typeno", "71","72","73","75","76","79"]);
    	map.setFilter('locals-lanes-styled', ["in", "typeno", "71","72","73","75","76","79"]);
	}
});

$('input[type=checkbox][name=hwy-data-layer]').on('change', function() {
	var label = $(this).parent("label");
	if(!label.hasClass("active")) {
		map.setPaintProperty($(this).val(), 'fill-extrusion-opacity', 0.75);
	} else {
		map.setPaintProperty($(this).val(), 'fill-extrusion-opacity', 0);
	}
});

$('input[type=radio][name=count-tod]').on('change', function(e) {
	var state = $(this).val();
	// drawValues(time);
	if(state === 'play'){
		animateCounts();
	}else if(state === 'stop'){
		clearInterval(animate);
	}  
	
})

var counts, countNumbers, maxCount, minCount;

var tod = 'am';
var countData = $.ajax({
    type:'GET',
    url:'https://wololo.co/dvrpc-tim-viewer/api/countlocations.php?t=a&fn=3&f0=am&f1=md&f2=pm',
    dataType:'JSON',
    data:{
    },
    beforeSend: function(){
    },
    success: function(data){
    	counts = data;

    	var countNumbers = counts.map(function(f){
			return f.data[0].am;
		});
		maxCount = Math.max(...countNumbers);
		minCount = Math.min(...countNumbers);

    	requestLocations();
    }
});

var timeOfDay = [
	'__AM0','__AM1','__AM2','__AM3','__AM4','__AM5','__AM6','__AM7','__AM8','__AM9','__AM10','__AM11','__PM0','__PM1','__PM2','__PM3','__PM4','__PM5','__PM6','__PM7','__PM8','__PM9','__PM10','__PM11'
]

var hour = 1, animate, subBin = 0;

// function frameAnimate(timestamp){
// 	if(subBin >= 1 && hour < 23 ){
// 		subBin = 0, hour++;
// 		$('#dat-time-label').html(timeOfDay[hour]);
// 	} else if(subBin >= 1 && hour == 23){
// 		subBin = 0, hour = 0;
// 	}
// 	if(hour < 23){
// 		var bin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[hour + 1]],["get", timeOfDay[hour]] ], subBin]] ],0,0,2500,1500];
// 		var colorBin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[hour + 1]],["get", timeOfDay[hour]] ], subBin]] ],
// 			0,
// 			'#fff200',
// 			2500,
// 			'#ED4264'
// 		];
// 		subBin += 0.166667;			
// 	}else if(hour === 23){
// 		var bin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[0]],["get", timeOfDay[hour]] ], subBin]] ],0,0,2500,1500];
// 		var colorBin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[0]],["get", timeOfDay[hour]] ], subBin]] ],
// 			0,
// 			'#fff200',
// 			2500,
// 			'#ED4264'
// 		];
// 		subBin += 0.166667;
// 	}

// 	map.setPaintProperty('count-circles', 'fill-extrusion-color', colorBin);
// 	map.setPaintProperty('count-circles', 'fill-extrusion-height', bin);
// 	requestAnimationFrame(frameAnimate)
// }

// build an animation of counts by interpolating 10min bins
// function animateCounts(timestamp) {
	
//     animate = setInterval(function(){
// 		if(subBin >= 1 && hour < 23 ){
// 			subBin = 0, hour++;
// 			$('#dat-time-label').html(timeOfDay[hour]);
// 		} else if(subBin >= 1 && hour == 23){
// 			subBin = 0, hour = 0;
// 		}
// 		if(hour < 23){
// 			var bin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[hour + 1]],["get", timeOfDay[hour]] ], subBin]] ],0,0,2500,1500];
// 			var colorBin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[hour + 1]],["get", timeOfDay[hour]] ], subBin]] ],
// 				0,
// 				'#fff200',
// 				2500,
// 				'#ED4264'
// 			];
// 			subBin += 0.166667;			
// 		}else if(hour === 23){
// 			var bin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[0]],["get", timeOfDay[hour]] ], subBin]] ],0,0,2500,1500];
// 			var colorBin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[0]],["get", timeOfDay[hour]] ], subBin]] ],
// 				0,
// 				'#fff200',
// 				2500,
// 				'#ED4264'
// 			];
// 			subBin += 0.166667;
// 		}

// 		map.setPaintProperty('count-circles', 'fill-extrusion-color', colorBin);
// 	  	map.setPaintProperty('count-circles', 'fill-extrusion-height', bin);
//     }, 200);
// }

function animateCounts(timestamp) {
	
    animate = setInterval(function(){
		if(subBin > 5 && hour < 23 ){
			subBin = 0, hour++;
			$('#dat-time-label').html(timeOfDay[hour]);
		} else if(subBin > 5 && hour == 23){
			subBin = 0, hour = 0;
		}
		// if(hour < 23){
			var tick = (subBin == 0) ?  '' : '-'+ subBin;
			var bin = ["interpolate",["exponential", 1],["number", ["get", timeOfDay[hour + tick]] ],0,0,2500,1500];
			var colorBin = ["interpolate",["exponential", 1],["number", ["get", timeOfDay[hour + tick]] ],
				0,
				'#fff200',
				2500,
				'#ED4264'
			];
			subBin += 1;			
		// }else if(hour === 23){
		// 	var bin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[0]],["get", timeOfDay[hour]] ], subBin]] ],0,0,2500,1500];
		// 	var colorBin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[0]],["get", timeOfDay[hour]] ], subBin]] ],
		// 		0,
		// 		'#fff200',
		// 		2500,
		// 		'#ED4264'
		// 	];
		// 	subBin += 0.166667;
		// }

		map.setPaintProperty('count-circles', 'fill-extrusion-color', colorBin);
	  	map.setPaintProperty('count-circles', 'fill-extrusion-height', bin);
    }, 100);
}

function processCountData(data){
	Object.keys(data.features).forEach(function (id) {
		timeOfDay.forEach(function(hour, i, allHours){
			if(i < 23){
				var base = data.features[id].properties[hour],
					next = data.features[id].properties[allHours[i+1]];
				var diff = next - base;
				for(var k = 1; k < 6; k++){
					var percent = k / 6;
					var newVar = hour + '-' + k;
					data.features[id].properties[newVar] = base + (percent * diff);
				}
			}
			if( i == 23){
				var base = data.features[id].properties[hour],
					next = data.features[id].properties[allHours[0]];
				var diff = next - base;
				for(var k = 1; k < 6; k++){
					var percent = k / 6;
					var newVar = hour + '-' + k;
					data.features[id].properties[newVar] = base + (percent * diff);
				}
			}
		})
	});

	return data;
}

var requestLocations = function(){
	$.ajax({
	    type:'GET',
	    url:'./lib/data/count_data.geojson',
	    dataType:'JSON',
	    data:{
	    },
	    beforeSend: function(){
	    },
	    success: function(data){
			var newData = processCountData(data);

			console.log(newData);

	        map.addSource("counts", {
		        type: "geojson",
		        data: newData
			});
			
		 	map.addLayer({
		        "id": "count-circles",

		        "source": "counts",
		        "type": 'fill-extrusion',
    				"paint": {
    					'fill-extrusion-opacity': 0,
    					'fill-extrusion-color': {
    						  property: '__AM0',
    						  type: 'exponential',
    						  stops: [
									[0, '#fff200'],
									[2500, '#ED4264']
								]
    					},
    					'fill-extrusion-height': [
							"interpolate",
							["exponential", 1],
							["number", ["get", "__AM0"]],
							0,
							0,
							2500,
							1500
						],
						'fill-extrusion-height-transition': {
							duration: 2500,
							delay: 0
						},
				}
		    });

		    $('#js-count-btn').removeClass('disabled');
		    map.on('click', 'count-circles', function (e) {
		        console.log(e.features);

		    });
	    }
});
}

