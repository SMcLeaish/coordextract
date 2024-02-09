"""Module for parsing GPX files and extracting geographical data.

This module provides functionality to parse GPX files,
extracting waypoints, trackpoints, and routepoints. 

Example usage:
    from gpx_parser import parse_gpx_geo_data
    
    waypoints, trackpoints, routepoints = parse_gpx_geo_data("path/to/your/file.gpx")
"""
import logging
from typing import Tuple, List, Optional, String
from lxml import etree

Coordinates = Tuple[float, float]
CoordinatesList = List[Coordinates]

def parse_point(point: etree._Element) -> Optional [Tuple[float, float]]:
    """
    Extracts the latitude and longitude from a GPX point element.
    Args:
        point: An lxml Element representing a GPX waypoint, trackpoint, or routepoint.
    Returns:
        A tuple of (latitude, longitude) as floats if the attributes are present and valid; None otherwise.
    """
    try:
        lat = point.get('lat')
        lon = point.get('lon')
        if lat is not None and lon is not None:
            return float(lat), float(lon)
    except ValueError as e:
        logging.error(f"Invalid coordinate value: {e}")
    return None
def parse_gpx_geo_data(gpx_file_path: String
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
    try: 
        with open(gpx_file_path, 'rb') as file:
            xml = etree.parse(file, parser)
    except IOError as e:
        logging.error(f"Error opening or reading file: {e}")
        return [], [], []
    gpx_version = xml.getroot().get("version")
    if gpx_version not in ["1.0", "1.1"]:
        logging.error(f"Unsupported GPX version: {gpx_version}")
        return [], [], []
    ns_map = {'gpx': f'http://www.topografix.com/GPX/{gpx_version}'}
    
    waypoints = [parse_point(wpt) for wpt in xml.findall('.//gpx:wpt', namespaces=ns_map) if parse_point(wpt) is not None]
    trackpoints = [parse_point(trkpt) for trkpt in xml.findall('.//gpx:trkpt', namespaces=ns_map) if parse_point(trkpt) is not None]
    routepoints = [parse_point(rtept) for rtept in xml.findall('.//gpx:rtept', namespaces=ns_map) if parse_point(rtept) is not None]

    return waypoints, trackpoints, routepoints
