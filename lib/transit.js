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
});
