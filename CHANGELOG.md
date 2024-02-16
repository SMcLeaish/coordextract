## Changelog

### v.0.1.0: 
* coordextract/parsers/gpx_parse.py : waypoints, trackpoints, routepoints = async_parse_gpx("path/to/your/file.gpx")
* returns a list of lat, long tuples sorted by waypoints, trackpoints, and routepoints

* coordextract/converters/latlon_to_mgrs_converter.py : latlon_to_mgrs(float, float)
* returns mgrs as a string

### v.0.1.1:
* added the following packages: coordextract/models, coordextract/factory. 
* made a new module in coordextract/factory to create objects from the pydantic class defined in coordextract/models
### v.0.2.0
* filehandler module, puts the pieces together. Calls the parser, converter, and point object and builds the object for export.
* coordextract cli tool 
### TODO
* output to JSON
* output to files 
* conversion for other filetypes: kml, csv, xlsx, json
