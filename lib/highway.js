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
	// var time = $(this).val();
	// drawValues(time);
  animateCounts(0);
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
    	// data.forEach(function(row) {
    	// 	_counts.push({'no': row.key.no, 'aadt': row.data[0].aadt});
    	// });
    	var countNumbers = counts.map(function(f){
			return f.data[0].am;
		});
		maxCount = Math.max(...countNumbers);
		minCount = Math.min(...countNumbers);

    	requestLocations();
    }
});


////////////////////////////////////////////////
/////////////    old block remove
////////////////////////////////////////
//
//
// // Get the percentage for a value
// function getPercentage(value) {
//   if (!Number(value)) {
//     return 0;
//   }
//
//   var totalDiff = maxCount - minCount,
//       valueDiff = value - minCount;
//   var percentage = valueDiff / totalDiff * 100;
//
//   percentage = Math.max(percentage, 0);
//   percentage = Math.min(percentage, 100);
//
//   return percentage;
// }
//
// // Get the color for a value depending on the percentage
// var begin = { red: 255, green: 242, blue: 0 };
// var end = { red: 237, green: 66, blue: 100 };
// function getColor(value) {
//   var percentage = getPercentage(value) / 100;
//
//   var red = begin.red + Math.floor(percentage * (end.red - begin.red));
//   var green = begin.green + Math.floor(percentage * (end.green - begin.green));
//   var blue = begin.blue + Math.floor(percentage * (end.blue - begin.blue));
//
//   return 'rgb(' + red + ',' + green + ',' + blue + ')';
// }
//
// // Get the categorical color stops for the areas
// function getColorStops() {
//   var stops = [];
//   Object.keys(counts).forEach(function (id) {
//     var value = counts[id].data[0][tod];
//
//     if (!value || isNaN(value)) {
//     	value = 0
//     }
//     var color = getColor(value, minCount, maxCount);
//     stops.push([counts[id].key.no, color]);
//   });
//
//   return stops;
// }
//
// // Get the height stops for the areas
// function getHeightStops() {
//   var stops = [ ];
//
//   Object.keys(counts).forEach(id => {
//     var value = counts[id].data[0][tod];
//
//     if (!value || isNaN(value)) {
//       value = 0
//     }
//
//     var percentage = Math.floor(getPercentage(value));
//     var height = percentage * 30;
//     stops.push([counts[id].key.no, height]);
//   });
//
//   return stops;
// }


//shitty test of animating counts
function animateCounts(timestamp) {

    var hour = 0;

    setInterval(function(){
      var bin = ["interpolate",["exponential", 1],["number", ["get", "__AM"+hour]],0,0,2500,1500];
      map.setPaintProperty('count-circles', 'fill-extrusion-height', bin);
      hour++;
    }, 1500);
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

	        map.addSource("counts", {
		        type: "geojson",
		        data: data
		    });

// @ remove old ref to count viz
		  //   var countNumbers = _counts.map(function(f){
		  //   	return f.aadt;
		  //   });

		  //   var maxCount = Math.max(...countNumbers);
		  //   var minCount = Math.min(...countNumbers);

		  //   var maxRadius = 20;
		  //   var minRadius = 4;

		 	// var rateOfChange = (maxRadius - minRadius) / (maxCount - minCount);
		 	// var radiusAtZero = maxRadius - (rateOfChange * maxCount);


		 	// var circleSize = function(volume) {
		 	// 	var radius = (rateOfChange * volume) + radiusAtZero;

		 	// 	return radius
		 	// }

		 	// var aadtVolume = ["match", ["get", "no"]];

		 	// _counts.forEach(function(row) {
		  //       var size = circleSize(row['aadt']);
		  //       aadtVolume.push(row["no"], size);
		  //   });

		 	// aadtVolume.push(10);

		 	map.addLayer({
		        "id": "count-circles",

		        "source": "counts",
		        "type": 'fill-extrusion',
    				"paint": {
    					'fill-extrusion-opacity': 0,
    					'fill-extrusion-color': {
    						  property: '__AM7',
    						  type: 'exponential',
    						  stops: [
                      [0, '#fff200'],
                      [2500, '#ED4264']
                  ]
    					},
    					// 'fill-extrusion-height': 40,
    					'fill-extrusion-height': [
                "interpolate",
                ["exponential", 1],
                ["number", ["get", "__AM7"]],
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
