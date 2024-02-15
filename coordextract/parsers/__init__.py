"""
This module provides functionality for parsing GPX files to extract geographical 
data, including waypoints, trackpoints, and routepoints. It supports both synchronous 
and asynchronous operations to accommodate different application needs.

The `parse_point` function extracts individual geographical points from GPX data, 
validating latitude and longitude values before returning them as tuples. This 
functionality underpins the more comprehensive `async_parse_gpx` function, which 
processes entire GPX files to return lists of validated waypoints, trackpoints, 
and routepoints.

Example usage:
    from mgrs_processing.parsers.gpx_parse import async_parse_gpx
    
    waypoints, trackpoints, routepoints = async_parse_gpx("path/to/your/file.gpx")
"""
from .gpx_parse import async_parse_gpx
__all__=["async_parse_gpx"]
