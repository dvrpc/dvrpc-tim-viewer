# DVRPC TIM Viewer  
*codenames: tart, peeping TIM*

This is an internal tool for exploring the inputs and outputs of the DVRPC Travel Improvement Model (TIM). Product is in early development.

## Front End
*Dependencies*
* Tileserver-php 
    * vector tile host, alternatives available
* Mapbox-gl JS
* ogr2ogr 
    * for data preparation and spatial transformations
* tippecanoe
    * for creation of Mbtiles
    * runs on Linux or OSX
* mbutils 
    * for final dump of Mbtiles for web server

## Back End
*Dependencies - Core*
* Python 2.7
    * psycopg2
    * numpy
* PostgreSQL 9.5
    * PostGIS 2.3+ (3rd party)
    * tablefunc (extension needs to be enabled)

*Dependencies - Utilities*
* Python 2.7
    * MS Access ODBC
        * pypyodbc [Github](https://github.com/jiangwen365/pypyodbc)
        * Microsoft Access Database Engine (for your flavour of Microsoft Office)
            Note: You may need to add the `/passive` switch to install e.g. `AccessDatabaseEngine_x64.exe /passive`


_This is not a formally supported or endorsed product of the DVRPC_