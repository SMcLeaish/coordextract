"""This module provides functionality for processing GPX files into
structured geographic data models. It leverages asynchronous parsing to
handle waypoints, trackpoints, and routepoints within GPX files,
converting them into a list of PointModel instances. Each PointModel
instance represents a geographic point with its latitude, longitude, and
converted Military Grid Reference System (MGRS) coordinates.

The module integrates components for parsing GPX files and converting geographic coordinates
to ensure efficient processing and accurate data representation.

Functions:
- process_gpx_to_point_models: Converts GPX file contents into a list of PointModel instances.
"""

import math
import logging
from coordextract.parsers.gpx_parse import async_parse_gpx
from coordextract.converters.latlon_to_mgrs_converter import latlon_to_mgrs
from coordextract.models.point import PointModel


async def process_gpx_to_point_models(gpx_file_path: str) -> list[PointModel]:
    """Asynchronously processes a GPX file, extracting waypoints,
    trackpoints, and routepoints, and converts them into a list of
    PointModel instances.

    Each geographic point is converted to MGRS format, and invalid points (with non-numeric
    coordinates) are logged and skipped. This function ensures that all valid points from
    the GPX file are accurately represented as PointModel instances, suitable for further
    processing or analysis.

    Args:
        gpx_file_path (str): The file path to the GPX file to be processed.

    Returns:
        list[PointModel]: A list of PointModel instances representing the processed geographic
        points.

    Raises:
        ValueError: If the GPX file cannot be parsed or if any points contain invalid coordinates.
    """

    waypoints, trackpoints, routepoints = await async_parse_gpx(gpx_file_path)
    points_with_types = {
        "waypoint": waypoints,
        "trackpoint": trackpoints,
        "routepoint": routepoints,
    }
    point_models = []
    for point_type, points in points_with_types.items():
        for point in points:
            latitude, longitude, additional_fields = point

            if math.isnan(latitude) or math.isnan(longitude):
                logging.warning(
                    "Skipping invalid point with attributes: %s, %s",
                    latitude, longitude
                )
                continue

            mgrs = latlon_to_mgrs(latitude, longitude)

            point_data = {
                "name": additional_fields.get("name") if additional_fields else None,
                "gpxpoint": point_type,
                "latitude": latitude,
                "longitude": longitude,
                "mgrs": mgrs
            }

            # If there are additional fields, update point_data with them
            if additional_fields:
                point_data.update(additional_fields)

            # Create PointModel instance
            point_model = PointModel(**point_data)
            point_models.append(point_model)
    return point_models