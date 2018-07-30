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
		"url": "https://tiles.dvrpc.org/data/dvrpc-tim-counts.json"
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

const bikeNetwork = {
	exists: false,

	show: function(){
		this.exists ? map.setPaintProperty('tim-bike-facilities', 'line-opacity', 1.0) : this.addLayer();
	},

	hide: function() {
		this.exists ? map.setPaintProperty('tim-bike-facilities', 'line-opacity', 0.0) : '';
	},

	addLayer: function(){
		map.addSource("bike-lanes", {
			"type": "vector",
			"url": "https://tiles.dvrpc.org/data/dvrpc-tim-bikes.json"
		});
		map.addLayer({
			"id": "tim-bike-facilities",
			"source": "bike-lanes",
			"source-layer": "tim-bike",
			"type": 'line',
			"paint": {
				"line-color": {"property": "bktyp",
					"stops": [
						[1, "#D271C3"], 
						[2, "#742C99"],
						[3, "#29C2EB"], 
						[4, "#54B947"],
						[5, "#ADACAA"]
					]
				},
				"line-width": {
					"base": 1,
					"stops": [
						[
							14,
							1.5
						],
						[
							15,
							3.5
						],
						[
							16,
							5
						]
					]
				}
			}
		}, 'interstate-motorway_shields');

		this.exists = true;
	}
	
}

const truckPerformance = {
	exists: false,

	visible: false,

	type: 'S',

	dirs: ['B','T','F'],

	timeMap: ['00','00','00','00','00','05','05','07','07','09','09','11','11','13','13','15','15','17','17','19','19','19','19','19'],

	color: function(time){
		var style =  {
			'S': {
				"property": this.type + this.timeMap[animation.hour],
				"type": "categorical",
				"stops": [
					['z', '#9c9c9c'],
					['k', '#730000'],
					['r', '#e60000'],
					['o', '#f07d02'],
					['a', '#ffcb0d'],
					['y', '#FF0'],
					['c', '#AF0'],
					['g', '#38a800']
				]
			},
			'T': {
				"property": this.type + this.timeMap[animation.hour],
				"type": "categorical",
				"stops": [
					['z', '#9c9c9c'],
					['g', '#38a800'],
					['y', '#ffcb0d'],
					['o', '#f07d02'],
					['r', '#e60000'],
					['k', '#730000']
					
				]
			}
		};
		console.log(style[this.type])
		for(var k = 0; k < this.dirs.length; k++ ){
			map.setPaintProperty('tp-'+ this.dirs[k], 'line-color', style[this.type]);
		}

	},

	show: function(){
		animation.togglePanel(1);
		truckPerformance.visible = true;
		legend.innerHTML = truckPerformance.type === 'S' ? tp_S_legend : tp_T_legend;
		this.exists ? this.toggleMap(1.0) : this.addLayer();
		
	},

	hide: function() {
		if(truckPerformance.visible === true){
			animation.togglePanel(-1);
			truckPerformance.visible = false;
		}
		this.exists ? this.toggleMap(0.0) : '';
	},

	toggleMap: function(opacity){
		for(var k = 0; k < this.dirs.length; k++ ){
			truckPerformance.color();
			map.setPaintProperty('tp-'+ this.dirs[k], 'line-opacity', opacity);
		}
	},
	addLayer: function(){
		map.addSource("truck-pm", {
			"type": "vector",
			"url": "https://tiles.dvrpc.org/data/dvrpc-pff-truck.json"
		});
		
		for(var i = 0; i < this.dirs.length; i++){
			var offset = (this.dirs[i] === 'B') ? 1.3 : 0;

			map.addLayer({
				"id": "tp-" + this.dirs[i],
				"source": "truck-pm",
				"source-layer": "truck-pm",
				"type": 'line',
				"filter": [
					"all",
					[
						"in",
						"DIR_TYPE",
						this.dirs[i]
					]
				],
				"layout": {
					"line-join": "round"
				},
				"paint": {
					"line-color": {
						"property": "S00",
						"type": "categorical",
						"stops": [
							['z', '#9c9c9c'],
							['k', '#730000'],
							['r', '#e60000'],
							['o', '#f07d02'],
							['a', '#ffcb0d'],
							['y', '#FF0'],
							['c', '#AF0'],
							['g', '#38a800']
						]
					},
					'line-opacity': 1.0,
					"line-width": {
						"base": 1,
						"stops": [
							[
								14,
								1.5
							],
							[
								15,
								3.5
							],
							[
								16,
								5
							]
						]
					},
					"line-offset": offset
				}
			}, 'interstate-motorway_shields')
		}

		this.exists = true;
	}
}

const tp_T_legend = '<h6>Truck Performance</h6>'+
	'<div id="pm-btns" class="btn-group btn-group-sm" role="group" >'+
	'<button type="button" class="btn btn-secondary toggle-pm" data-mode="S">Speed</button>'+
	'<button type="button" class="btn btn-secondary active" data-mode="T">TTI</button>'+
	'</div>'+
	'<div id="hp_legend_TTI" class="hp_legend_wrapper">'+
	'<div class="hp_label">Travel Time Index Value</div>'+
	'<div class="hp_legend hp_z">no data</div>'+
	'<div class="hp_legend hp_g">< 1.1</div>'+
	'<div class="hp_legend hp_a">1.1 - 1.5</div>'+
	'<div class="hp_legend hp_o">1.5 - 2.0</div>'+
	'<div class="hp_legend hp_r">2.0 - 3.0</div>'+
	'<div class="hp_legend hp_k">> 3.0</div>'+
	'</div>';
	

const tp_S_legend = '<h6>Truck Performance</h6>'+
	'<div id="pm-btns" class="btn-group btn-group-sm" role="group" >'+
	'<button type="button" class="btn btn-secondary active" data-mode="S">Speed</button>'+
	'<button type="button" class="btn btn-secondary toggle-pm" data-mode="T">TTI</button>'+
	'</div>'+
	'<div id="hp_legend_Speed" class="hp_legend_wrapper">'+
	'<div class="hp_label">Average Speed (MPH)</div>'+
	'<div class="hp_legend hp_z">no data</div>'+
	'<div class="hp_legend hp_k">< 10</div>'+
	'<div class="hp_legend hp_r">10 - 20</div>'+
	'<div class="hp_legend hp_o">20 - 30</div>'+
	'<div class="hp_legend hp_a">30 - 40</div>'+
	'<div class="hp_legend hp_y">40 - 50</div>'+
	'<div class="hp_legend hp_c">50 - 60</div>'+
	'<div class="hp_legend hp_g">> 60</div>'+
	'</div>';
	
$('#legend').on('click','.toggle-pm', function(){
	var pm = this.dataset.mode;
	truckPerformance.type = pm;
	truckPerformance.color();
	legend.innerHTML = truckPerformance.type === 'S' ? tp_S_legend : tp_T_legend;
});

const bike_legend = '<h6>Bike Network Facility</h6> '+
	'<ul class="l-list">'+
	'<li><div class="l-line b-one"></div>Sharrow </li>'+
	'<li><div class="l-line b-two"></div>Bike Lane </li>'+
	'<li><div class="l-line b-three"></div>Buffered Bike Lane </li>'+
	'<li><div class="l-line b-four"></div>Trail (bike/ped only) </li>'+
	'<li><div class="l-line b-five"></div>Connector (bike-friendly street) </li>'+
	'</ul>';

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

const tl_legend = '<h6>Lane Count</h6><i class="fa fa-minus" style="color:#fef0d9"></i>&nbsp;&nbsp;1 lane<br/><i class="fa fa-minus" style="color:#fdbb84"></i>&nbsp;&nbsp;2 lane<br/><i class="fa fa-minus" style="color:#fc8d59"></i>&nbsp;&nbsp;3 lane<br/><i class="fa fa-minus" style="color:#e34a33"></i>&nbsp;&nbsp;4+ lane<br/>';

var legend = document.getElementById('legend');

function clearHighwayStyle(){
	legend.innerHTML = "";
	bikeNetwork.hide();
	truckPerformance.hide();
	map.setFilter('highways-urban-fc-styled', ["all", ["in", "typeno", " "], ["in", "fed_fclass",11,12,14,16,17,19,99] ]);
	map.setFilter('highways-rural-fc-styled', ["all", ["in", "typeno", " "], ["in", "fed_fclass",1,2,6,7,8,9] ]);
	map.setFilter('locals-urban-fc-styled', ["all", ["in", "typeno", " "], ["in", "fed_fclass",11,12,14,16,17,19,99] ]);
	map.setFilter('locals-rural-fc-styled', ["all", ["in", "typeno", " "], ["in", "fed_fclass",1,2,6,7,8,9] ]);

	map.setFilter('highways-lanes-styled', ["in", "typeno", " "]);
	map.setFilter('locals-lanes-styled', ["in", "typeno", " "]);
}


$('input[type=radio][name=hwy-render-state]').on('change', function() {
	clearHighwayStyle();
	switch ($(this).val()){
		case 'hwy-tl-style':
			legend.innerHTML = tl_legend;
			map.setFilter('highways-lanes-styled', ["!in", "typeno", "71","72","73","75","76","79"]);
			map.setFilter('locals-lanes-styled', ["in", "typeno", "71","72","73","75","76","79"]);
			break;
		case 'hwy-fc-style':
			legend.innerHTML = fc_legend;
			map.setFilter('highways-urban-fc-styled', ["all", ["!in", "typeno", "71","72","73","75","76","79"], ["in", "fed_fclass",11,12,14,16,17,19,99] ]);
			map.setFilter('highways-rural-fc-styled', ["all", ["!in", "typeno", "71","72","73","75","76","79"], ["in", "fed_fclass",1,2,6,7,8,9] ]);
			map.setFilter('locals-urban-fc-styled', ["all", ["in", "typeno", "71","72","73","75","76","79"], ["in", "fed_fclass",11,12,14,16,17,19,99] ]);
			map.setFilter('locals-rural-fc-styled', ["all", ["in", "typeno", "71","72","73","75","76","79"], ["in", "fed_fclass",1,2,6,7,8,9] ]);
			break;
		case 'bike-net':
			legend.innerHTML = bike_legend;
			bikeNetwork.show();
			break;
		case 'hwy-tp-style':
			truckPerformance.show();
			break;

	}
});

// traffic count viz toggle
$('input[type=checkbox][name=hwy-data-layer]').on('change', function() {
	var label = $(this).parent("label");
	if(!label.hasClass("active")) {
		animation.paintCounts();
		map.setPaintProperty($(this).val(), 'fill-extrusion-opacity', 0.75);
		map.flyTo({
			pitch: 60,
			easing(t) {
				return t;
			}
		});
		animation.countsVisible = true;
		animation.togglePanel(1);
	} else {
		map.setPaintProperty($(this).val(), 'fill-extrusion-opacity', 0);
		map.flyTo({
			pitch: 0,
			easing(t) {
				return t;
			}
		});
		animation.countsVisible = false;
		animation.togglePanel(-1);
		if(icon.hasClass('active')){playHandler();}
	}
});

var icon = $('.play');

function playHandler (){
	if(icon.hasClass('active')){
		animation.stop();
	}else {
		animation.start();
	}
   icon.toggleClass('active');
   return false;
}

icon.click(function() {
	playHandler();
});

var speeds = $('#speed-btns button')

speeds.click(function(e){
	animation.speed = this.dataset.speed;
	for (k = 0; k < speeds.length; k++) {
		$(speeds[k]).removeClass('active');
	}
	$(this).addClass('active')
})

var timeOfDay = [
	'__AM0','__AM1','__AM2','__AM3','__AM4','__AM5','__AM6','__AM7','__AM8','__AM9','__AM10','__AM11','__PM0','__PM1','__PM2','__PM3','__PM4','__PM5','__PM6','__PM7','__PM8','__PM9','__PM10','__PM11'
]

const animation = {
	hour: 0,
	mins: 0,
	timePerFrame: 10,
	speed: 1,
	animate : '',
	animatedLayers: 0,
	countsVisible: false,

	togglePanel: function(count){
		animation.animatedLayers += count;

		if(animation.animatedLayers > 0){
			document.getElementById('time-panel').classList.remove('hidden');
		} else {
			document.getElementById('time-panel').classList.add('hidden');
		}
	},

	start: function(time) {
		this.animate = setInterval(function(){
			animation.updateTime();

			animation.countsVisible ? animation.paintCounts() : '';
			truckPerformance.visible ? truckPerformance.color() : '';
			
			animation.minCounter();
			
		}, 150);
	},

	stop: function(){
		clearInterval(this.animate);
	},

	minCounter: function(){
		animation.mins += ((animation.timePerFrame * animation.speed) / 60);
	},

	updateTime: function(){
		
		if(animation.mins >= 0.99 && animation.hour < 23 ){
			animation.mins = 0, animation.hour++;
			
		} else if(animation.mins >= 0.99 && animation.hour == 23){
			animation.mins = 0, animation.hour = 0;
		}
		var suffix = (animation.hour >= 12) ? ' PM' : ' AM';
		var twelveHour = (animation.hour <= 12) ? animation.hour : animation.hour - 12;
		twelveHour = (twelveHour === 0) ? 12 : twelveHour;
	
		var minutes = (animation.mins * 60).toLocaleString('en');

		minutes = ('0' + minutes).slice(-2);
		var hourString = twelveHour +':'+ minutes + suffix;
		
		$('#dat-time-label').html(hourString);
	},

	paintCounts: function(){
		if(animation.hour < 23){
			var bin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[animation.hour]], ["*", ["-",["get", timeOfDay[animation.hour + 1]],["get", timeOfDay[animation.hour]] ], animation.mins]] ],0,0,2500,1500];
			var colorBin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[animation.hour]], ["*", ["-",["get", timeOfDay[animation.hour + 1]],["get", timeOfDay[animation.hour]] ], animation.mins]] ],
				0,
				'#fff200',
				2500,
				'#ED4264'
			];			
		}else if(animation.hour === 23){
			var bin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[animation.hour]], ["*", ["-",["get", timeOfDay[0]],["get", timeOfDay[animation.hour]] ], animation.mins]] ],0,0,2500,1500];
			var colorBin = ["interpolate",["exponential", 1],["number", ["+", ["get", timeOfDay[animation.hour]], ["*", ["-",["get", timeOfDay[0]],["get", timeOfDay[animation.hour]] ], animation.mins]] ],
				0,
				'#fff200',
				2500,
				'#ED4264'
			];
		}
	
		map.setPaintProperty('count-circles', 'fill-extrusion-color', colorBin);
		map.setPaintProperty('count-circles', 'fill-extrusion-height', bin);
	}
}