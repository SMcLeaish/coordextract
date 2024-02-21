"""Module for parsing GPX files and extracting geographical data.

Example usage:
    from mgrs_processing.parsers.gpx_parse import async_parse_gpx

    waypoints, trackpoints, routepoints = async_parse_gpx("path/to/your/file.gpx")
"""

import math
from typing import Tuple, Optional, Any
import aiofiles
from lxml import etree

Coordinates = Tuple[float, float, Optional[dict[str, str | Any]]]
CoordinatesList = list[Coordinates]


def parse_point(
    point: etree._Element,
) -> Tuple[float, float, Optional[dict[str, str | Any]]]:
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
        extra_fields = {}
        for child in point:
            tag = etree.QName(child).localname
            extra_fields[tag] = child.text
        if lat is not None and lon is not None:
            return float(lat), float(lon), extra_fields
    except Exception as e:
        raise ValueError("Invalid coordinate value encountered.") from e
    return (math.nan, math.nan, extra_fields)


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
            raise ValueError("GPX file is empty or unreadable")
        try:
            xml = etree.fromstring(xml_data, parser)
        except etree.XMLSyntaxError as e:
            raise ValueError(f"GPX file contains invalid XML: {e}") from e
    except OSError as e:
        raise OSError(f"Error accessing file at {gpx_file_path}: {e}") from e
    except RuntimeError as e:
        raise RuntimeError(f"Unexpected error processing file {gpx_file_path}: {e}") from e

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
