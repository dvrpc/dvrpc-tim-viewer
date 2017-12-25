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

    <nav class="navbar navbar-default">
        <div class="container-fluid">
            <!-- Brand and toggle get grouped for better mobile display -->
            <div class="navbar-header">
                <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="#">Peeping TIM</a>
            </div>

            <!-- Collect the nav links, forms, and other content for toggling -->
            <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
                <ul class="nav navbar-nav">
                    <li class="active">
                        <a href="#">Highway<span class="sr-only">(current)</span></a>
                    </li>
                    <li>
                        <a href="transit.htm">Transit</a>
                    </li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Dropdown <span class="caret"></span></a>
                        <ul class="dropdown-menu">
                            <li><a href="#">Action</a></li>
                            <li><a href="#">Another action</a></li>
                            <li><a href="#">Something else here</a></li>
                            <li role="separator" class="divider"></li>
                            <li><a href="#">Separated link</a></li>
                            <li role="separator" class="divider"></li>
                            <li><a href="#">One more separated link</a></li>
                        </ul>
                    </li>
                </ul>
                <!--
                <form class="navbar-form navbar-left">
                    <div class="form-group">
                        <input type="text" class="form-control" placeholder="Search">
                    </div>
                    <button type="submit" class="btn btn-default">Submit</button>
                </form>
                -->
                <ul class="nav navbar-nav navbar-right">
                    <li><a href="#">Link</a></li>
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown" role="button" aria-haspopup="true" aria-expanded="false">Dropdown <span class="caret"></span></a>
                        <ul class="dropdown-menu">
                        <li><a href="#">Action</a></li>
                        <li role="separator" class="divider"></li>
                        <li><a href="#">Separated link</a></li>
                        </ul>
                    </li>
                </ul>
            </div><!-- /.navbar-collapse -->
        </div><!-- /.container-fluid -->
    </nav>

    <div id='box'>

        <div id='bar' class='col-md-3'>
            <ul class="nav nav-tabs" role="tablist">
                <li role="presentation" class="active"><a href="#layers" aria-controls="layers" role="tab" data-toggle="tab">Layers</a></li>
                <li role="presentation"><a href="#attributes" aria-controls="attributes" role="tab" data-toggle="tab">Attributes</a></li>
                <li role="presentation"><a href="#analysis" aria-controls="analysis" role="tab" data-toggle="tab">Analysis</a></li>
            </ul>
            <div class="tab-content">
                <div role="tabpanel" class="tab-pane active" id="layers">
                    <h4>Base Layers</h4>
                    <form>
                    <ul id="baselayers">
                        <li><input type="radio" name="hwy-render-state" value="hwy-no-style" checked>No Style</li>
                        <li><input type="radio" name="hwy-render-state" value="hwy-fc-style">Functional Class</li>
                        <li><input type="radio" name="hwy-render-state" value="hwy-tl-style">Travel Lane Count</li>
                    </ul>
                    </form>
                    <h4>Data Layers</h4>
                    <form>
                    <ul id="datalayerslist">
                        <!-- <li class="ui-state-default"><span class="ui-icon ui-icon-arrowthick-2-n-s"></span><input type="checkbox">Item 1</li> -->
                    </ul>
                    </form>
                </div>
                <div role="tabpanel" class="tab-pane" id="attributes"></div>
                <div role="tabpanel" class="tab-pane" id="analysis"></div>
            </div>
            <div id="legend"></div>
            <div id="layerList"></div>
            <pre id="propertyList"></pre>
        </div>
        <div id='map' class='col-md-9'></div>
    </div>

    <script src="https://code.jquery.com/jquery-3.2.1.min.js" integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=" crossorigin="anonymous"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js" integrity="sha384-Dziy8F2VlJQLMShA6FHWNul/veM9bCkRUaLqr199K94ntO5QUrLJBEbYegdSkkqX" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tether/1.4.0/js/tether.min.js" integrity="sha384-DztdAPBWPRXSA/3eYEEUWrWCy7G5KFbe8fFjk5JAIxUYHKkDx6Qin1DkWx51bBrb" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
    <script src='https://api.mapbox.com/mapbox-gl-js/v0.42.0/mapbox-gl.js'></script>
    <script src='lib/config.js' type="text/javascript"></script>
    <script src='lib/highway.js' type="text/javascript"></script>
    <script src='lib/_debug.js' type="text/javascript"></script>

</body>
</html>