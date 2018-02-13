# API

## Available Data/(partial) Database Schema

**/api/schema.php**

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
connectors.php
countlocations.php
crosswalks.php
demandsegments.php
detectors.php
directions.php
linerouteitems.php
lineroutes.php
lines.php
links.php
linktypes.php
mainlines.php
mainnodes.php
mainturns.php
mainzones.php
modes.php
nodes.php
operators.php
paths.php
pathsets.php
screenlines.php
signalcontrols.php
signalgroups.php
stages.php
stopareas.php
stoppoints.php
stops.php
territories.php
tickettypes.php
timeprofileitems.php
timeprofiles.php
tollsystems.php
tsystems.php
turns.php
validdayscont.php
vehiclecombinations.php
vehiclejourneyitems.php
vehiclejourneys.php
vehicleunits.php
vehijouneysections.php
zones.php

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

## Skim Matrices

**/api/matrices.php**

HTTP Method: `GET`/`POST`

Parameters:
* m: `INTEGER` Matrix number
* t: `TEXT` Time of Day {`AM`,`MD`,`PM`,`NT`}


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
* oz(n): `INTEGER`
* dz(n): `INTEGER`

Return Value:
  * Standard Feature Collection GeoJSON
