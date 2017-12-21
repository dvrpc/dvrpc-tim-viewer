<?php
    $allowed_ips = array(
        "10.1.1.166",   // T
        "10.1.1.96",    // R
        "10.1.1.191",   // L
        "10.1.1.86"     // B
    );
    $found = false;
    foreach ($allowed_ips as $ip) {
        if ($_SERVER['REMOTE_ADDR'] == $ip) {
            $found = true;
            break;
        }
    }
    if (!$found) {
        http_response_code(404);
        die("");
    }
?>
<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'/>
    <title>TIM Viewer</title>
    <meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
    <style>
        body { margin:0; padding:0; }

        #map { position:absolute; top:56px; bottom:0; width:100%; }

        #legend {
			bottom: 40px;
		    right: 20px;
		    z-index: 10000;
		    position: absolute;
		    display: block;
		    padding: 10px;
		    border: 1px solid #ddd;
		    box-sizing: border-box;
		    background-color: #fff;
		}
    </style>
    
	<link href='https://api.mapbox.com/mapbox-gl-js/v0.40.1/mapbox-gl.css' rel='stylesheet' />
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/css/bootstrap.min.css" integrity="sha384-rwoIResjU2yc3z8GV/NPeZWAv56rSmLldC3R/AZzGRnGxQQKnKkoFVhFQhNUwEyJ" crossorigin="anonymous">
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" />

	<style>
		
	</style>
</head>

<body>
	<nav class="navbar navbar-toggleable-md navbar-inverse bg-inverse fixed-top">
      <button class="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" data-target="#navbarsExampleDefault" aria-controls="navbarsExampleDefault" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <a class="navbar-brand" href="#">Peeping TIM</a>

      <div class="collapse navbar-collapse" id="navbarsExampleDefault">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item active">
            <a class="nav-link" href="#">Highway <span class="sr-only">(current)</span></a>
          </li>
          <li class="navbar-nav">
          		<a class="nav-link" href="transit.htm">Transit </a>
          </li>
        </ul>
      </div>
    </nav>
	<div id='map'></div>
	<div style="position:absolute; right:20px; top:75px">
	  <div id="style-selector" class="btn-group btn-group-vertical" data-toggle="buttons">
	    <label style="margin-bottom: .2rem;" class="btn btn-md btn-block well btn-primary active">
	      <input type="radio" name="hwy-render-state" value="hwy-no-style"> No Style
	    </label>
	    <label style="margin-bottom: .2rem;" class="btn btn-md btn-block well btn-primary">
	      <input type="radio" name="hwy-render-state" value="hwy-fc-style"> Functional Class
	    </label>
	    <label style="margin-bottom: .2rem;" class="btn btn-md btn-block well btn-primary">
	      <input type="radio" name="hwy-render-state" value="hwy-tl-style"> Travel Lane Count
	    </label>
	  </div>
	</div>
	<div id="legend"></div>
	<div id="layerList"></div>
    <pre id="propertyList"></pre>


    <script src="https://code.jquery.com/jquery-3.1.1.slim.min.js" integrity="sha384-A7FZj7v+d/sdmMqp/nOQwliLvUsJfDHW+k9Omg/a/EheAdgtzNs3hpfag6Ed950n" crossorigin="anonymous"></script>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/tether/1.4.0/js/tether.min.js" integrity="sha384-DztdAPBWPRXSA/3eYEEUWrWCy7G5KFbe8fFjk5JAIxUYHKkDx6Qin1DkWx51bBrb" crossorigin="anonymous"></script>
	<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/js/bootstrap.min.js" integrity="sha384-vBWWzlZJ8ea9aCX4pEW3rVHjgjt7zpkNpZk+02D9phzyeVkE+jo0ieGizqPLForn" crossorigin="anonymous"></script>
    <script src='https://api.mapbox.com/mapbox-gl-js/v0.40.1/mapbox-gl.js'></script>
	<script src='lib/config.js' type="text/javascript"></script>
	<script src='lib/highway.js' type="text/javascript"></script>
    <script src='lib/_debug.js' type="text/javascript"></script>
</body>
</html>