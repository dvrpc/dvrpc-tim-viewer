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

map.on('load', function(){
	map.addSource("counts", {
		"type": "vector",
		"url": "https://a.michaelruane.com/data/dvrpc-tim-counts.json"
	});
	map.addLayer({
		"id": "count-circles",
		"source": "counts",
		"source-layer": "count_data",
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
});

const fc_legend = '<h6>Federal Functional Classification</h6><div class="legend-col">'+
	'<b>Urban</b>'+
	'<ul class="l-list">'+
	'<li><div class="l-line c-one"></div>Principal Arterial Interstate </li>'+
	'<li><div class="l-line c-two"></div>Principal Arterial Other Freeway </li>'+
	'<li><div class="l-line c-three"></div>Other Principal Arterial </li>'+
	'<li><div class="l-line c-four"></div>Minor Arterial </li>'+
	'<li><div class="l-line c-five"></div>Collector </li>'+
	'<li><div class="l-line c-seven"></div>Local </li>'+
	'<li><div class="l-line c-eight"></div>Ramp</li>'+
	'</ul>'+
	'</div>'+
	'<div class="legend-col">'+
	'<b>Rural</b>'+
	'<ul class="l-list">'+
	'<li><div class="l-line l-dash c-one"></div>Principal Arterial Interstate </li>'+
	'<li><div class="l-line l-dash c-two"></div>Principal Arterial Other Freeway </li>'+
	'<li><div class="l-line l-dash c-four"></div>Minor Arterial </li>'+
	'<li><div class="l-line l-dash c-five"></div>Major Collector </li>'+
	'<li><div class="l-line l-dash c-six"></div>Minor Collector </li>'+
	'<li><div class="l-line l-dash c-seven"></div>Local </li>'+
	'</ul>'+
	'</div>';

const tl_legend = '<i class="fa fa-minus" style="color:#fef0d9"></i>&nbsp;&nbsp;1 lane<br/><i class="fa fa-minus" style="color:#fdbb84"></i>&nbsp;&nbsp;2 lane<br/><i class="fa fa-minus" style="color:#fc8d59"></i>&nbsp;&nbsp;3 lane<br/><i class="fa fa-minus" style="color:#e34a33"></i>&nbsp;&nbsp;4+ lane<br/>';

var legend = document.getElementById('legend');

function clearHighwayStyle(){
	legend.innerHTML = "";
	map.setFilter('highways-urban-fc-styled', ["all", ["in", "typeno", " "], ["in", "fed_fclass",11,12,14,16,17,19,99] ]);
	map.setFilter('highways-rural-fc-styled', ["all", ["in", "typeno", " "], ["in", "fed_fclass",1,2,6,7,8,9] ]);
	map.setFilter('locals-urban-fc-styled', ["all", ["in", "typeno", " "], ["in", "fed_fclass",11,12,14,16,17,19,99] ]);
	map.setFilter('locals-rural-fc-styled', ["all", ["in", "typeno", " "], ["in", "fed_fclass",1,2,6,7,8,9] ]);

	map.setFilter('highways-lanes-styled', ["in", "typeno", " "]);
	map.setFilter('locals-lanes-styled', ["in", "typeno", " "]);
}


$('input[type=radio][name=hwy-render-state]').on('change', function() {
	if($(this).val() == 'hwy-no-style'){
		clearHighwayStyle();
	} else if($(this).val() == 'hwy-fc-style'){
		clearHighwayStyle()
    	legend.innerHTML = fc_legend;
		map.setFilter('highways-urban-fc-styled', ["all", ["!in", "typeno", "71","72","73","75","76","79"], ["in", "fed_fclass",11,12,14,16,17,19,99] ]);
		map.setFilter('highways-rural-fc-styled', ["all", ["!in", "typeno", "71","72","73","75","76","79"], ["in", "fed_fclass",1,2,6,7,8,9] ]);
		map.setFilter('locals-urban-fc-styled', ["all", ["in", "typeno", "71","72","73","75","76","79"], ["in", "fed_fclass",11,12,14,16,17,19,99] ]);
		map.setFilter('locals-rural-fc-styled', ["all", ["in", "typeno", "71","72","73","75","76","79"], ["in", "fed_fclass",1,2,6,7,8,9] ]);
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
		map.flyTo({
			pitch: 60,
			easing(t) {
				return t;
			}
		});
	} else {
		map.setPaintProperty($(this).val(), 'fill-extrusion-opacity', 0);
		map.flyTo({
			pitch: 0,
			easing(t) {
				return t;
			}
		});
	}
});

$('input[type=radio][name=count-tod]').on('change', function(e) {
	var state = $(this).val();
	// drawValues(time);
	if(state === 'play'){
		animateCounts(hour);
	}else if(state === 'stop'){
		clearInterval(animate);
	}  
	
})


// @REMOVE

// var counts, countNumbers, maxCount, minCount;

// var tod = 'am';
// var countData = $.ajax({
//     type:'GET',
//     url:'https://wololo.co/dvrpc-tim-viewer/api/countlocations.php?t=a&fn=3&f0=am&f1=md&f2=pm',
//     dataType:'JSON',
//     data:{
//     },
//     beforeSend: function(){
//     },
//     success: function(data){
//     	counts = data;

//     	var countNumbers = counts.map(function(f){
// 			return f.data[0].am;
// 		});
// 		maxCount = Math.max(...countNumbers);
// 		minCount = Math.min(...countNumbers);
//     }
// });

var timeOfDay = [
	'__AM0','__AM1','__AM2','__AM3','__AM4','__AM5','__AM6','__AM7','__AM8','__AM9','__AM10','__AM11','__PM0','__PM1','__PM2','__PM3','__PM4','__PM5','__PM6','__PM7','__PM8','__PM9','__PM10','__PM11'
]

var hour = 1, animate, subBin = 0, timePerFrame = 5;

// build an animation of counts by interpolating 10min bins
function animateCounts(timestamp) {
	
    animate = setInterval(function(){

		if(subBin >= 1 && hour < 23 ){
			subBin = 0, hour++;
			
		} else if(subBin >= 1 && hour == 23){
			subBin = 0, hour = 0;
		}
		var suffix = (hour >= 12) ? ' PM' : ' AM';
		var twelveHour = (hour <= 12) ? hour : hour - 12;
		twelveHour = (twelveHour === 0) ? 12 : twelveHour;

		var minutes = (subBin * 60).toLocaleString('en');
		minutes = ('0' + minutes).slice(-2);
		var hourString = twelveHour +':'+ minutes + suffix;

		$('#dat-time-label').html(hourString);
		
		if(hour < 23){
			var bin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[hour + 1]],["get", timeOfDay[hour]] ], subBin]] ],0,0,2500,1500];
			var colorBin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[hour + 1]],["get", timeOfDay[hour]] ], subBin]] ],
				0,
				'#fff200',
				2500,
				'#ED4264'
			];
			subBin += (timePerFrame / 60);			
		}else if(hour === 23){
			var bin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[0]],["get", timeOfDay[hour]] ], subBin]] ],0,0,2500,1500];
			var colorBin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[hour]], ["*", ["-",["get", timeOfDay[0]],["get", timeOfDay[hour]] ], subBin]] ],
				0,
				'#fff200',
				2500,
				'#ED4264'
			];
			subBin += (timePerFrame / 60);
		}

		map.setPaintProperty('count-circles', 'fill-extrusion-color', colorBin);
	  	map.setPaintProperty('count-circles', 'fill-extrusion-height', bin);
	  
    }, 150);
}