# coordextract

* Library to convert latitudes and longitudes in json, gpx, kml, csv, or xlsx to mgrs and export as csv, json, or xlsx

## Changelog

### v.0.1.0: 
* coordextract/parsers/gpx_parse.py : waypoints, trackpoints, routepoints = async_parse_gpx("path/to/your/file.gpx")
* returns a list of lat, long tuples sorted by waypoints, trackpoints, and routepoints

* coordextract/converters/latlon_to_mgrs_converter.py : latlon_to_mgrs(float, float)
* returns mgrs as a string

### TODO
* conversion for other filetypes: kml, csv, xlsx, json
* cli tool 
