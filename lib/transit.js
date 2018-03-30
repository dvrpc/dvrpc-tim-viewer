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

//populate line selections
var lineOptions = [];
var systems = [];
var lineRequest = $.get('http://wololo.co/dvrpc-tim-viewer/api/line.php?t=a&fn=2&f0=mainlinename&f1=shortname')
    .done(function(lines) {
        Object.keys(lines).forEach(function(i) {
            if (systems.indexOf(lines[i].data[0].mainlinename) < 0) {
                systems.push(lines[i].data[0].mainlinename)
            }
            // console.log(i, lines[i].key.name)
            // lineOptions[lines[i].key.name] = lines[i].data[0]
        });
        createDropdown();
        lineOptions = lines;
    });

function createDropdown(){
    console.log("createDropdown()");
    var systemDropdown = document.getElementById('system-dropdown')
    var frag = document.createDocumentFragment(),
        elOption,
        sortedSystems = systems.sort();
    sortedSystems.forEach(function(item){
        elOption = frag.appendChild(document.createElement('option'));
        elOption.text = item;
        elOption.val = item;
    });
    systemDropdown.appendChild(frag);
}

function findObjectByKey(array, key, value) {
    for (var i = 0; i < array.length; i++) {
        if (array[i][key] === value) {
            return array[i];
        }
    }
    return null;
}

function populateLineDropdown(system){
    console.log("populateLineDropdown()");
    var lines = [], fullLines;
    var lineDropdown = document.getElementById('line-dropdown'),
        frag = document.createDocumentFragment(),
        elOption;

    elOption = frag.appendChild(document.createElement('option'));
    elOption.text = "Select a line";

    for( var i = 0; i < lineOptions.length; i++ ){
        if(lineOptions[i].data[0].mainlinename === system){
            lines.push(lineOptions[i].key.name);
        }
    }
    lines = lines.sort();
    lines.forEach(function(line){
        for (var i = 0; i < lineOptions.length; i++) {
            if (lineOptions[i].key.name === line) {
                elOption = frag.appendChild(document.createElement('option'));
                elOption.text = lineOptions[i].data[0].shortname;
                elOption.value = line;
            }
        }
    });
    lineDropdown.innerHTML = "",
    lineDropdown.appendChild(frag);
    lineDropdown.disabled = false;
}

var lineData = {};
var tempLineData = $.get('http://wololo.co/dvrpc-tim-viewer/api/line.php?t=t&fn=3&f0=line_boardings&f1=person_trips&f2=pass_miles')
    .done(function(data) {
        Object.keys(data).forEach(function(key) {
            var nameID = data[key].key.name;
            lineData[nameID] = data[key].data;
        });
    });

$('#system-dropdown').on('change', function(e){
    var selected = $(this).val()
    populateLineDropdown(selected);
});

$('#line-dropdown').on('change', function(e){
    var selected = $(this).val()
    showLineResults(selected);
});

$('#route-submit').on('click', function(e){
    e.preventDefault();
    showLineResults($('#route').val());
});

function showLineResults(lineName){
    console.log("showLineResults()");
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
    console.log(bounds);
    map.fitBounds(bounds, {
        padding: 20
    });
    downloadLineroute(lineName);
    populateDemo(lineName);
    setupAnimoot(coordinates);
}

function downloadLineroute(line) {
    //build query
    console.log("downloadLineroute()");
    var payload = JSON.stringify({
        "netobj": "line",
        "keys": {"name": line},
        "netfields": ["mainlinename", "shortname", "person_trips_am", "pass_miles_am"  ]
      });
    var results = $.post('http://wololo.co/dvrpc-tim-viewer/api/line.php', payload)
    .done(function(data){
        console.log('hi');
        //success motherfucker, now do shit
        $('#dat-shortname').html(data.netpayload.shortname)
        $('#dat-mainlinename').html(data.netpayload.mainlinename)
    });
}

function formatNumber(num){
  return num.toLocaleString('en-US',{maximumFractionDigits:0});
}

function populateDemo(name){
    console.log("populateDemo()");
    var data = lineData[name];
    Object.keys(data).forEach(function(key) {
        var tod = data[key].tod;
        $('#'+tod+'-line_boardings').html(formatNumber(data[key].line_boardings))
        $('#'+tod+'-person_trips').html(formatNumber(data[key].person_trips))
        $('#'+tod+'-pass_miles').html(formatNumber(data[key].pass_miles))
    });
}

//

document.addEventListener("animoot-next-frame", function(e) {
    setTimeout(_animoot, 1000);
});
var animootNextFrame = new CustomEvent("animoot-next-frame", {});

var objects = {};
var counter = 0;
var coordinates;

function pointOnCircle(index) {
    index = index % coordinates.length;
    return {
        "type": "Point",
        "coordinates": coordinates[index]
    };
}

function verifyPosition(counter) {
    var continue = false;
    Object.keys(animoot_objects).forEach(function(id) {
        
    });
    document.dispatchEvent(animootNextFrame);
}

function _animoot() {
    counter += 1;
    map.getSource('point').setData(pointOnCircle(counter));
    // requestAnimationFrame(verifyPosition);
    requestAnimationFrame(function (){});
}

function setupAnimoot(_coordinates) {
    coordinates = _coordinates;
    map.addSource('point', {
        "type": "geojson",
        "data": pointOnCircle(0)
    });
    map.addLayer({
        "id": "point",
        "source": "point",
        "type": "circle",
        "paint": {
            "circle-radius": 10,
            "circle-color": "#007cbf"
        }
    });
    _animoot();
}
