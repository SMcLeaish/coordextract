# coordextract

* Library to convert latitudes and longitudes in json, gpx, kml, csv, or xlsx to mgrs and export as csv, json, or xlsx

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
* coordextract cli tool 
usage: `coordextract -f yourfile.gpx` prints an object with all latitude and longitude and mgrs from a gpx file
### TODO
* conversion for other filetypes: kml, csv, xlsx, json
* cli tool 


 *This repository is mirrored at [https://github.com/SMcLeaish/coordextract/](https://github.com/SMcLeaish/coordextract/) from [https://gitlab.com/smcleaish/coordextract](https://gitlab.com/smcleaish/coordextract) and uses gitlab CI*
