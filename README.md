# mgrs-processing

* Package to convert latitudes and longitudes in json, csv, or xlsx to mgrs 

### v.0.1.0: 
* mgrs_processing/parsers/gpx_parse.py : waypoints, trackpoints, routepoints = async_parse_gpx("path/to/your/file.gpx")
* returns a list of lat, long tuples sorted by waypoints, trackpoints, and routepoints
