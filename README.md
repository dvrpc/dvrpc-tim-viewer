# DVRPC TIM Viewer  
*codenames: tart, peeping TIM*

This is an internal tool for exploring the inputs and outputs of the DVRPC Travel Improvement Model (TIM). Product is in early development.

## Viewer Roadmap 
This roadmap is organized by network system and feature priority. 

### Highway
- [x] Federal functional class  (__1__)
- [x] Number of lanes  (__1__)  *requires offset visualization for readability*
- [x] Traffic counts  (__1__)
- [x] Average speed: *hourly*  (__2__)
- [x] Travel time index: *hourly*  (__2__)
- [ ] AADT by segment  (__2__)
- [ ] Volume or V/C *simulated*  (__2__)

### Bike
- [x] Facility type  (__1__)
- [ ] Slope  (__1__)

### Transit
- [x] Line route  (__1__)
- [ ] Stop location  (__1__)
- [ ] Headway/frequency  (__1__)
- [ ] Line boardings  (__3__)
- [ ] Stop boardings  (__4__)
- [ ] Average traffic speed  (__4__)

### Zone and travel data
- [x] Population  (__1__)
- [x] Households  (__1__)
- [x] Employment totals  (__1__)
- [x] Employment by sector  (__1__)
- [x] Number of POIs  (__2__)  *available but require metadata to implement*
- [x] OD Desrire lines  (__3__)
- [x] Top travel destinations  (__1__)

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
[API documentation](/api/README.md)
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
        * pypyodbc [PyPi](https://pypi.python.org/pypi/pypyodbc) [Github](https://github.com/jiangwen365/pypyodbc)
        * Microsoft Access Database Engine (for your flavour of Microsoft Office)
            Note: You may need to add the `/passive` switch to install e.g. `AccessDatabaseEngine_x64.exe /passive`



_This is not a formally supported or endorsed product of the DVRPC_
