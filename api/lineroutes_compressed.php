<?php
    include('_functions.php');
    ob_start("ob_gzhandler");
    header('Content-Encoding: gzip');
    echo GetGeoJSON("lineroutes", $_GET);
?>