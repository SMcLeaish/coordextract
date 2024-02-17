"""
The coordextract package provides utilities for extracting and converting geographic 
coordinates from various formats. It simplifies the process of working with geospatial 
data, particularly focusing on GPX parsing and coordinate conversion to the Military 
Grid Reference System (MGRS).

Key Features:
- Parsing GPX files to extract waypoints, trackpoints, and routepoints.
- Converting latitude and longitude coordinates to MGRS strings.

These functionalities are exposed at the top level for convenient access, supporting both 
synchronous and asynchronous workflows.

Example Usage:
    # Parsing GPX files
    from coordextract.parsers import async_parse_gpx
    waypoints, trackpoints, routepoints = async_parse_gpx("path/to/gpx_file.gpx")

    # Converting coordinates to MGRS
    from coordextract.converters import latlon_to_mgrs
    mgrs_string = latlon_to_mgrs(34.6195, -117.8319)

This package aims to be a helpful tool in geospatial analysis, mapping applications, and any project 
requiring efficient handling of GPS and MGRS data formats.
"""

from .handler import filehandler

__all__ = ["filehandler"]
