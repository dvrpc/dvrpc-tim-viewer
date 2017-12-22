<?php
    include('_functions.php');
    echo gzencode(GetGeoJSON("lineroutes", $_GET));
?>