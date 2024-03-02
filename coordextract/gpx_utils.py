"""Module for parsing GPX files and extracting point data."""

import asyncio
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Optional, Tuple

import aiofiles
from lxml import etree

from .point import PointModel

Coordinates = Tuple[float, float, dict[str, str | Any]]
CoordinatesList = Optional[list[Coordinates]]


class GPXUtils:
    """Class for parsing GPX files and extracting point data."""

    def __init__(self, concurrency: bool = True):
        self.concurrency = concurrency

    async def process_gpx(
        self, gpx_file_path: Optional[Path]
    ) -> list[PointModel]:
        """Asynchronously reads the contents of a GPX file with aiofiles
        and calls the _parse_gpx method to process the file concurrently
        using concurrent.futures.ProcessPoolExecutor.

        Args:
            gpx_file_path (str): The file path to the GPX file to be
            processed.

        Returns:
            pointmodels: The list of PointModel objects extracted from
                the GPX file.

        Raises:
            OSError: If an error occurs while reading the file.
        """
        if gpx_file_path is None:
            raise ValueError("No file path provided")
        async with aiofiles.open(gpx_file_path, "rb") as file:
            xml_data = await file.read()
        if self.concurrency:
            try:
                loop = asyncio.get_running_loop()
                with ProcessPoolExecutor() as pool:
                    concurrent = True
                    point_models = await loop.run_in_executor(
                        pool, GPXUtils.parse_gpx, concurrent, xml_data
                    )
            except OSError as e:
                raise OSError(
                    f"Error accessing file at {gpx_file_path}: {e}"
                ) from e
            return point_models
        try:
            concurrent = False
            point_models = GPXUtils.parse_gpx(concurrent, xml_data)
        except OSError as e:
            raise OSError(
                f"Error accessing file at {gpx_file_path}: {e}"
            ) from e
        return point_models

    @staticmethod
    def parse_gpx(concurrent: bool, xml_data: bytes) -> list[PointModel]:
        """Function that receives xml data and returns a list of
        PointModel.

        Args:
        gpx_file_path (str): Path to the GPX file to be parsed.
        Returns:
        pointmodels: The list of PointModel objects extracted from the
            GPX file.
        """
        parser = etree.XMLParser(
            resolve_entities=False, no_network=True, huge_tree=False
        )

        if not xml_data.strip():
            raise ValueError("GPX file is empty or unreadable")
        try:
            xml = etree.fromstring(xml_data, parser)
        except etree.XMLSyntaxError as e:
            raise ValueError(f"GPX file contains invalid XML: {e}") from e

        root_tag = xml.tag
        namespace_uri = root_tag[root_tag.find("{") + 1 : root_tag.find("}")]
        ns_map = {"gpx": namespace_uri}
        waypoints = [
            GPXUtils._parse_point(wpt)
            for wpt in xml.findall(".//gpx:wpt", namespaces=ns_map)
            if GPXUtils._parse_point(wpt) is not None
        ]
        trackpoints = [
            GPXUtils._parse_point(trkpt)
            for trkpt in xml.findall(".//gpx:trkpt", namespaces=ns_map)
            if GPXUtils._parse_point(trkpt) is not None
        ]
        routepoints = [
            GPXUtils._parse_point(rtept)
            for rtept in xml.findall(".//gpx:rtept", namespaces=ns_map)
            if GPXUtils._parse_point(rtept) is not None
        ]
        waypoints = waypoints if waypoints is not None else []
        trackpoints = trackpoints if trackpoints is not None else []
        routepoints = routepoints if routepoints is not None else []

        points_with_types = {
            "waypoint": waypoints,
            "trackpoint": trackpoints,
            "routepoint": routepoints,
        }
        point_models = GPXUtils._build_gpx_point_models(
            points_with_types, concurrent
        )
        return point_models

    @staticmethod
    def _build_gpx_point_models(
        points_with_types: dict[str, list[Coordinates | None]],
        concurrent: bool,
    ) -> list[PointModel]:
        point_models = []
        for point_type, points in points_with_types.items():
            for point in points:
                if isinstance(point, (list, tuple)) and len(point) == 3:
                    latitude, longitude, additional_fields = point
                    if (
                        point_type is not None
                        and additional_fields is not None
                    ):
                        additional_fields["point_type"] = point_type
                    if (
                        concurrent is not None
                        and additional_fields is not None
                    ):
                        additional_fields["concurrent"] = concurrent
                    point_model = PointModel.build(
                        latitude,
                        longitude,
                        additional_fields or {},
                    )
                if point_model is not None:
                    point_models.append(point_model)
        return point_models

    @staticmethod
    def _parse_point(point: etree._Element) -> Optional[Coordinates]:
        """Extracts the latitude and longitude from a GPX point element.

        Args:
            point: An lxml Element representing a GPX waypoint,
                trackpoint, or routepoint.
        Returns:
            A tuple of [latitude, longitude] as floats if the attributes
                are present
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
        except ValueError as e:
            raise ValueError(
                f"Invalid coordinate value encountered: {e}"
            ) from e
        return None
