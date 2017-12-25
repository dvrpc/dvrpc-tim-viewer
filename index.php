<?php
    $allowed_ips = array(
        "::1",          // IPv6 Loopback
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

    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap-theme.min.css" integrity="sha384-rHyoN1iRsVXV4nD0JutlnGaslCJuC7uwjduW9SVrLvRYooPp2bWYgmgJQIXwl/Sp" crossorigin="anonymous">
    <link href='https://api.mapbox.com/mapbox-gl-js/v0.42.0/mapbox-gl.css' rel='stylesheet' />
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css" />
    <link rel="stylesheet" href="css/css.css" />
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

        <div id='box'>
        <div id='bar' class='col-md-3'>
            <ul class="nav nav-tabs" role="tablist">
                <li role="presentation" class="active"><a href="#home" aria-controls="layers" role="tab" data-toggle="tab">Layers</a></li>
                <li role="presentation"><a href="#profile" aria-controls="attributes" role="tab" data-toggle="tab">Attributes</a></li>
            </ul>
            <div class="tab-content">
                <div role="tabpanel" class="tab-pane active" id="layers"></div>
                <div role="tabpanel" class="tab-pane" id="attributes"></div>
            </div>
        </div>
        <div id='map' class='col-md-9'></div>

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
        
        </div>


    <script src="https://code.jquery.com/jquery-3.2.1.min.js" integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tether/1.4.0/js/tether.min.js" integrity="sha384-DztdAPBWPRXSA/3eYEEUWrWCy7G5KFbe8fFjk5JAIxUYHKkDx6Qin1DkWx51bBrb" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
    <script src='https://api.mapbox.com/mapbox-gl-js/v0.42.0/mapbox-gl.js'></script>
    <script src='lib/config.js' type="text/javascript"></script>
    <script src='lib/highway.js' type="text/javascript"></script>
    <script src='lib/_debug.js' type="text/javascript"></script>

</body>
</html>