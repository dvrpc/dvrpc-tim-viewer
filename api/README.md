# API

## Available Data/(partial) Database Schema

**/api/schema.php**

HTTP Method: `GET`

Parameters:
    No parameters

Return value:
    JSON containing a list of table definitions.
    Each item/table definition is an associative array with two keys:
        t: (TEXT) Table Name
        fs: (LIST) Field definition list
    Each item/field definition is an associative array with two keys:
        f: (TEXT) Field Name
        key: (BOOLEAN) ID field flag

## Attributes

*

HTTP Method: GET

Parameters:
    t:
        a - Attributes

Return Value:

## Tables with geometry

--------------------|
connectors.php
countlocations.php
mainzones.php
nodes.php
screenlines.php
stopareas.php
stoppoints.php
stops.php
territories.php
zones.php

HTTP Method: GET

Parameters:
    t:
        g - Geometry/GeoJSON
    g:
        p - Point
        l - Line
        g - Polygon
    bbx0:
    bbx1:
    bby0:
    bby1:
        (Optional) Bounding Box Coordinates - WGS 84::EPSG 4326

Return value:
    Standard Feature Collection GeoJSON

## Analysis

** /api/desirelines.php **

HTTP Method: POST

Parameters:
    t:
        s - Simple point to point lines
        ddl - Delaunay Triangle Network desire lines
        vddl - Voronoi Polygon + Delaunay Triangle Network desire lines
    bbx0:
    bbx1:
    bby0:
    bby1:
        (Optional) Bounding Box Coordinates - WGS 84::EPSG 4326

Return Value:
    Standard Feature Collection GeoJSON
