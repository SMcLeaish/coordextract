# coordextract

* Package to parse latitudes and longitudes in json, gpx, kml, csv, or xlsx and convert to mgrs 

### v.0.1.0: 
* mgrs_processing/parsers/gpx_parse.py : waypoints, trackpoints, routepoints = async_parse_gpx("path/to/your/file.gpx")
* returns a list of lat, long tuples sorted by waypoints, trackpoints, and routepoints
