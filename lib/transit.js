mapboxgl.accessToken = mbconfig.token;

var map = new mapboxgl.Map({
  container: 'map',
  center: [-75.14, 39.95],
  zoom: 12,
  style: 'lib/map_styles/transit.json',
  hash: 'true',

});

var reference = new mapboxgl.Map({
	container: 'reference',
	center: [-75.14, 39.95],
  	zoom: 8,
  	style: 'lib/map_styles/reference.json',
  	interactive: false,

})

// navigation control
var nav = new mapboxgl.NavigationControl();
map.addControl(nav, 'top-left');

var lineData = {};
var tempLineData = $.get('http://wololo.co/dvrpc-tim-viewer/api/line.php?t=t&fn=3&f0=line_boardings&f1=person_trips&f2=pass_miles')
  .done(function(data) {
    Object.keys(data).forEach(function(key) {
      var nameID = data[key].key.name;
      lineData[nameID] = data[key].data
      
    });
  });



$('#route-submit').on('click', function(e){
  e.preventDefault();
	var lineName = $('#route').val();
	map.setFilter('transit-lines', ["in", "linename", lineName]);
	map.setFilter('transit-labels', ["in", "linename", lineName]);
	
	var relatedFeatures = reference.querySourceFeatures('tim_transit', {
        sourceLayer: 'transit_lines',
        filter: ['in', 'linename',  lineName]
    });

    var coordinates = [];
    
    relatedFeatures.forEach(function(feature){
    	coordinates.push.apply(coordinates,feature.geometry.coordinates);
    });

	var bounds = coordinates.reduce(function (bounds, coord) {
	    return bounds.extend(coord);
	}, new mapboxgl.LngLatBounds(coordinates[0], coordinates[0]));
	
	map.fitBounds(bounds, {
	    padding: 20
	});

    downloadLineroute(lineName);

    populateDemo(lineName);
});

function downloadLineroute(line) {
    
    //build query
    var payload = JSON.stringify({
        "netobj": "line",
        "keys": {"name": line},
        "netfields": ["mainlinename", "shortname", "person_trips_am", "pass_miles_am"  ]
      });
    var results = $.post('http://wololo.co/dvrpc-tim-viewer/api/line.php', payload)
    .done(function(data){
        //success motherfucker, now do shit
        $('#dat-shortname').html(data.netpayload.shortname)
        $('#dat-mainlinename').html(data.netpayload.mainlinename)
    }); 

}

function formatNumber(num){
  return num.toLocaleString('en-US',{maximumFractionDigits:0});
}

function populateDemo(name){
  var data = lineData[name];
  Object.keys(data).forEach(function(key) {
    var tod = data[key].tod;
    $('#'+tod+'-line_boardings').html(formatNumber(data[key].line_boardings))
    $('#'+tod+'-person_trips').html(formatNumber(data[key].person_trips))
    $('#'+tod+'-pass_miles').html(formatNumber(data[key].pass_miles))
  })
}