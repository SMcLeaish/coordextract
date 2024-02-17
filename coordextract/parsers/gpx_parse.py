"""Module for parsing GPX files and extracting geographical data.

Example usage:
    from mgrs_processing.parsers.gpx_parse import async_parse_gpx

    waypoints, trackpoints, routepoints = async_parse_gpx("path/to/your/file.gpx")
"""

import math
from typing import Tuple
import logging
import aiofiles
from lxml import etree

Coordinates = Tuple[float, float]
CoordinatesList = list[Coordinates]


def parse_point(point: etree._Element) -> Tuple[float, float]:
    """Extracts the latitude and longitude from a GPX point element.

    Args:
    point: An lxml Element representing a GPX waypoint, trackpoint, or routepoint.
    Returns:
    A tuple of [latitude, longitude] as floats if the attributes are present
    and valid; None otherwise.
    """
    try:
        lat = point.get("lat")
        lon = point.get("lon")
        if lat is not None and lon is not None:
            return float(lat), float(lon)
    except ValueError:
        logging.exception("Invalid coordinate value encountered.")
    return (math.nan, math.nan)


async def async_parse_gpx(
    gpx_file_path: str,
) -> Tuple[CoordinatesList, CoordinatesList, CoordinatesList]:
    """Function that receives a GPX file as input and returns lists of
    waypoints, trackpoints, and routepoints as tuples of [latitude,
    longitude].

    Args:
    gpx_file_path (str): Path to the GPX file to be parsed.
    Returns:
    Three lists of tuples: waypoints, trackpoints, and routepoints.
    """
    parser = etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=False)
    try:
        async with aiofiles.open(gpx_file_path, "rb") as file:
            xml_data = await file.read()
        if not xml_data.strip():
            logging.error("GPX file is empty or unreadable: %s", gpx_file_path)
            return [], [], []
        # xml_data_str = xml_data.decode('utf-8')
        # debug unit test error "data must be string"
        xml = etree.fromstring(xml_data, parser)
    except OSError:
        logging.exception("Error opening or reading file")
        return [], [], []
    except etree.XMLSyntaxError:
        logging.exception("XML syntax error in the file.")
        return [], [], []

    root_tag = xml.tag
    namespace_uri = root_tag[root_tag.find("{") + 1 : root_tag.find("}")]
    ns_map = {"gpx": namespace_uri}
    waypoints = [
        parse_point(wpt)
        for wpt in xml.findall(".//gpx:wpt", namespaces=ns_map)
        if parse_point(wpt) is not None
    ]
    trackpoints = [
        parse_point(trkpt)
        for trkpt in xml.findall(".//gpx:trkpt", namespaces=ns_map)
        if parse_point(trkpt) is not None
    ]
    routepoints = [
        parse_point(rtept)
        for rtept in xml.findall(".//gpx:rtept", namespaces=ns_map)
        if parse_point(rtept) is not None
    ]

    return waypoints, trackpoints, routepoints
