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

from coordextract.parsers.gpx_parse import async_parse_gpx
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
    waypoints = waypoints if waypoints is not None else []
    trackpoints = trackpoints if trackpoints is not None else []
    routepoints = routepoints if routepoints is not None else []

    points_with_types = {
        "waypoint": waypoints,
        "trackpoint": trackpoints,
        "routepoint": routepoints,
    }

    point_models = []
    for point_type, points in points_with_types.items():
        for point in points:
            if isinstance(point, (list, tuple)) and len(point) == 3:
                latitude, longitude, additional_fields = point
                point_model = PointModel.create_from_gpx_data(
                    point_type, latitude, longitude, additional_fields or {}
                )
            if point_model is not None:
                point_models.append(point_model)
    return point_models
