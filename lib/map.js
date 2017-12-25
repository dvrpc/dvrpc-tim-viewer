mapboxgl.accessToken = mbconfig.token;

var map = new mapboxgl.Map({
  container: 'map',
  center: [-75.14, 39.95],
  zoom: 12,
  style: 'pff_style.json',
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