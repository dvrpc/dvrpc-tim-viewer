# API

## Available Data/(partial) Database Schema

**/api/schema/**

HTTP Method: `GET`

Parameters:
* No parameters

Return value:
* JSON containing a list of table definitions.
* Each item/table definition is an associative array with two keys:
  * `t`: `TEXT` Table Name
  * `fs`: `LIST` Field definition list
* Each item/field definition is an associative array with two keys:
  * `f`: `TEXT` Field Name
  * `key`: `BOOLEAN` ID field flag
  * `tod`: `BOOLEAN` Temporal field flag

## Tables with Attributes

**/api/***|
----------|
connectors/
countlocations/
linerouteitems/
lineroutes/
lines/
links/
linktypes/
nodes/
screenlines/
stopareas/
stoppoints/
stops/
territories/
timeprofileitems/
timeprofiles/
vehiclejourneyitems/
vehiclejourneys/
zones/

HTTP Method: `GET`

Parameters:
* t: `TEXT`
  * `a` - Static Attributes
  * `t` - Temporal Attributes

Return Value:

## Tables with geometry

**/api/*** |
-----------|
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

HTTP Method: `GET`

Parameters:
* t: `TEXT`
  * `g` - Geometry/GeoJSON
* g: `TEXT`
  * `p` - Point
  * `l` - Line
  * `g` - Polygon
* bbx0: `FLOAT`
* bbx1: `FLOAT`
* bby0: `FLOAT`
* bby1: `FLOAT`
  * (Optional) Bounding Box Coordinates `WGS 84::EPSG 4326`

Return value:
  * Standard Feature Collection GeoJSON

## Matrices

**/api/matrices.php**

HTTP Method: `GET`/`POST`

Parameters:
* m: `INTEGER` Matrix number
* z(n): `INTEGER` Zone Numbers


## Analysis

**/api/desirelines.php**

HTTP Method: `POST`

Parameters:
* t: `TEXT`
  * `s` - Simple point to point lines
  * `ddl` - Delaunay Triangle Network desire lines
  * `vddl` - Voronoi Polygon + Delaunay Triangle Network desire lines
* m: `INTEGER`
  * `2000` - Car trip table
  * `2100` - Transit trip table
* tod(n): `TEXT`
  * `AM`, `MD`, `PM`, `NT`
* oz(n): `INTEGER` Origin Zones
* dz(n): `INTEGER` Desination Zones

Return Value:
  * Standard Feature Collection GeoJSON
