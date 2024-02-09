"""Module for parsing GPX files and extracting geographical data.

This module provides functionality to parse GPX files,
extracting waypoints, trackpoints, and routepoints. 

Example usage:
    from gpx_parser import parse_gpx_geo_data
    
    waypoints, trackpoints, routepoints = parse_gpx_geo_data("path/to/your/file.gpx")
"""
from typing import Tuple, List, Any
from lxml import etree

Coordinates = Tuple[float, float]
CoordinatesList = List[Coordinates]

def parse_gpx_geo_data(gpx_file_path: Any
    )-> Tuple[CoordinatesList, CoordinatesList, CoordinatesList]:
    """
    Function that receives a GPX file as input and returns lists of waypoints, trackpoints, and routepoints.
    Each point is represented as a tuple of latitude and longitude.

    Args:
    - gpx_file_path (str): Path to the GPX file to be parsed.

    Returns:
    - Tuple containing three lists of tuples (float, float): waypoints, trackpoints, and routepoints.
    """
    parser = etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False)
    with open(gpx_file_path, 'rb') as file:
        xml = etree.parse(file, parser)
    gpx_version = xml.getroot().get("version")
    if gpx_version == "1.0":
        ns_map = {'gpx': 'http://www.topografix.com/GPX/1/0'}
    elif gpx_version == "1.1":
        ns_map = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    else:
        raise ValueError(f"Unsupported GPX version: {gpx_version}")
    waypoints: List[Tuple[float, float]] = []
    trackpoints: List[Tuple[float, float]] = []
    routepoints: List[Tuple[float, float]] = []
    for wpt in xml.findall('.//gpx:wpt', namespaces=ns_map):
        waypoints.append((float(wpt.get('lat')), float(wpt.get('lon'))))
    for trkpt in xml.findall('.//gpx:trkpt', namespaces=ns_map):
        trackpoints.append((float(trkpt.get('lat')), float(trkpt.get('lon'))))
    for rtept in xml.findall('.//gpx:rtept', namespaces=ns_map):
        routepoints.append((float(rtept.get('lat')), float(rtept.get('lon'))))
    return waypoints, trackpoints, routepoints
