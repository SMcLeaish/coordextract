from typing import Optional, Tuple, Any
from pathlib import Path
from abc import ABC, abstractmethod
import mimetypes
import os
import json
import aiofiles
import asyncio
from concurrent.futures import ProcessPoolExecutor
from lxml import etree
from magika.magika import Magika  # type: ignore
from magika.types import MagikaResult  # type: ignore
from .point import PointModel


class CoordExtract(ABC):
    """Abstract base class for input/output handlers."""

    def __init__(
        self, filepath: Optional[Path] = None, concurrency: Optional[bool] = False
    ):
        """Initializes the CoordExtract with an optional filename.

        Args:
            filename (Optional[Path]): The filename to be processed. Defaults to None.
        """
        self.filename = filepath
        self.concurrency = concurrency

    @abstractmethod
    async def process_input(self) -> Optional[list[PointModel]]:
        """Abstract method to process input data."""

    @abstractmethod
    async def process_output(
        self, point_models: list[PointModel], indentation: Optional[int] = None
    ) -> Optional[str]:
        """Abstract method to process output data.

        Args:
            data: The data to be processed.
            indentation (Optional[int]): The indentation level for the output. Defaults to None.
        """

    @classmethod
    async def process_coords(
        cls,
        input_argument: Path,
        output_argument: Optional[Path] = None,
        indentation: Optional[int] = None,
        concurrency: Optional[bool] = False,
    ) -> Optional[str]:
        """Processes a geographic data file and outputs the results to a
        specified file or stdout.

        This function serves as the core processing workflow, invoking input handling to parse and
        convert geographic data from the specified input file and then using output handling to
        serialize and write the data to a JSON file or stdout with optional indentation. It provides
        user feedback on the process success or reasons for failure.

        Args:
            inputfile (Path): The path to the input file containing geographic data to be processed.
            outputfile (Optional[Path]): The path to the output JSON file where the processed data
            should be saved. If None, the output will be printed to stdout.

            indentation (Optional[int]): The number of spaces used for JSON output indentation.
            Defaults to 2

        Raises:
            ValueError: If the file type is unsupported or the file type cannot be determined.
        """
        input_handler = cls.factory(input_argument, concurrency)
        filehandler_result = await input_handler.process_input()
        if filehandler_result is not None and output_argument is not None:
            output_handler = cls.factory(output_argument)
            if output_argument is not None:
                output_handler.filename = output_argument
                await output_handler.process_output(filehandler_result, indentation)
                return None
        elif filehandler_result is not None:
            output_handler = cls.factory()
            output_str = await output_handler.process_output(
                filehandler_result, indentation
            )
            if output_str is not None:
                return output_str
        else:
            raise ValueError(
                "Error: File handler returned None. Check the input file path\
                or filehandler implementation."
            )
        return None

    @classmethod
    def factory(
        cls, filename: Optional[Path] = None, concurrency: Optional[bool] = False
    ) -> "CoordExtract":
        """Factory function to create an appropriate CoordExtract based
        on the file type.

        Args:
            factory_argument (Optional[Path]): The path to the file. Defaults to None.

        Returns:
            CoordExtract: An instance of the appropriate CoordExtract subclass.

        Raises:
            ValueError: If the file type is unsupported or the file type cannot be determined.
        """
        if filename is None:
            return JSONHandler()
        mimetype, magika_result = cls._get_mimetype(filename)
        if mimetype is None or magika_result is None:
            raise ValueError(f"Could not determine the filetype of: {filename}")
        if (
            mimetype == "application/gpx+xml"
            and magika_result.output.mime_type == "text/xml"
        ):
            return GPXHandler(filename, concurrency)
        if mimetype == "application/json":
            return JSONHandler(filename)
        raise ValueError(f"Unsupported file type for {filename}")

    @staticmethod
    def _get_mimetype(filename: Path) -> Tuple[Optional[str], Optional[MagikaResult]]:
        """Get the mimetype of a file using the filename extension and
        Magika library.

        Args:
            filename (Path): The path to the file.

        Returns:
            Tuple[Optional[str], Optional[MagikaResult]]: A tuple containing the mimetype
            and the MagikaResult object.
        """
        m = Magika()
        mimetype, _ = mimetypes.guess_type(str(filename))
        magika_result = m.identify_path(filename)
        return mimetype, magika_result


class GPXHandler(CoordExtract):
    """Input/output handler for GPX files."""

    Coordinates = Optional[Tuple[float, float, Optional[dict[str, str | Any]]]]
    CoordinatesList = Optional[list[Coordinates]]

    async def process_input(self) -> list[PointModel]:
        """Processes the input GPX file and returns a list of PointModel
        objects.

        Returns:
            list[PointModel]: The list of PointModel objects extracted from the GPX file.
        """
        print(self.concurrency)
        if self.concurrency:
            return await self._concurrent_process_gpx(str(self.filename))
        return await self._process_gpx(str(self.filename))

    async def process_output(
        self, point_models: list[PointModel], indentation: Optional[int] = None
    ) -> None:
        """Raises a NotImplementedError as GPX output processing is not
        supported.

        Args:
            point_models (list[PointModel]): The data to be processed.
            indentation (Optional[int]): The indentation level for the output. Defaults to None.

        Raises:
            NotImplementedError: GPX output processing is not supported.
        """
        raise NotImplementedError(
            "Only GPX input is supported, GPX output processing is not supported."
        )

    async def _concurrent_process_gpx(self, gpx_file_path: str) -> list[PointModel]:
        """Asynchronously reads the contents of a GPX file and returns
        the raw XML data.

        Args:
            gpx_file_path (str): The file path to the GPX file to be processed.

        Returns:
            bytes: The raw XML data from the GPX file.

        Raises:
            OSError: If an error occurs while reading the file.
        """
        try:
            async with aiofiles.open(gpx_file_path, "rb") as file:
                xml_data = await file.read()
            loop = asyncio.get_running_loop()
            with ProcessPoolExecutor() as pool:
                point_models = await loop.run_in_executor(
                    pool, self._parse_gpx, xml_data
                )
        except OSError as e:
            raise OSError(f"Error accessing file at {gpx_file_path}: {e}") from e
        return point_models

    async def _process_gpx(self, gpx_file_path: str) -> list[PointModel]:
        """Asynchronously reads the contents of a GPX file and returns
        the raw XML data.

        Args:
            gpx_file_path (str): The file path to the GPX file to be processed.

        Returns:
            bytes: The raw XML data from the GPX file.

        Raises:
            OSError: If an error occurs while reading the file.
        """
        try:
            async with aiofiles.open(gpx_file_path, "rb") as file:
                xml_data = await file.read()
                point_models = self._parse_gpx(xml_data)
        except OSError as e:
            raise OSError(f"Error accessing file at {gpx_file_path}: {e}") from e
        return point_models

    def _parse_gpx(self, xml_data: bytes) -> list[PointModel]:
        """Function that receives a GPX file as input and returns lists
        of waypoints, trackpoints, and routepoints as tuples of
        [latitude, longitude].

        Args:
        gpx_file_path (str): Path to the GPX file to be parsed.
        Returns:
        Three lists of tuples: waypoints, trackpoints, and routepoints.
        """
        print("PID: ", os.getpid())
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
            self._parse_point(wpt)
            for wpt in xml.findall(".//gpx:wpt", namespaces=ns_map)
            if self._parse_point(wpt) is not None
        ]
        trackpoints = [
            self._parse_point(trkpt)
            for trkpt in xml.findall(".//gpx:trkpt", namespaces=ns_map)
            if self._parse_point(trkpt) is not None
        ]
        routepoints = [
            self._parse_point(rtept)
            for rtept in xml.findall(".//gpx:rtept", namespaces=ns_map)
            if self._parse_point(rtept) is not None
        ]
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

    def _parse_point(self, point: etree._Element) -> Optional[Coordinates]:
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
        except ValueError as e:
            raise ValueError(f"Invalid coordinate value encountered: {e}") from e
        return None


class JSONHandler(CoordExtract):
    """Input/output handler for JSON files."""

    async def process_input(self) -> None:
        """Raises a NotImplementedError as JSON input processing is not
        supported.

        Raises:
            NotImplementedError: JSON input processing is not supported.
        """
        raise NotImplementedError(
            "Only JSON output is supported, JSON input processing is not supported."
        )

    async def process_output(
        self, point_models: list[PointModel], indentation: Optional[int] = None
    ) -> Optional[str]:
        """Processes the output data and returns the JSON representation
        of the PointModel objects.

        Args:
            point_models (list[PointModel]): The list of PointModel objects to be processed.
            indentation (Optional[int]): The indentation level for the output. Defaults to None.

        Returns:
            Optional[str]: The JSON representation of the PointModel objects.
        """
        if self.filename is not None:
            await self._point_models_to_json(
                point_models, str(self.filename), indentation
            )
            return None
        return await self._point_models_to_json(point_models, None, indentation)

    async def _point_models_to_json(
        self,
        point_models: list[PointModel],
        filename: Optional[str] = None,
        indentation: Optional[int] = None,
    ) -> Optional[str]:
        """Serializes a list of PointModel instances to JSON format and
        writes to a file or prints to stdout.

        This function converts a list of PointModel instances into a JSON-formatted string with the
        specified indentation level. If a filename is provided, the JSON string is written to the
        specified file. Otherwise, the JSON string is printed to stdout.

        Args:
            point_models (list[PointModel]): A list of PointModel instances to be serialized.
            filename (Optional[str]): The path to the output file where the JSON string
            should be saved. If None, the JSON string is printed to stdout instead.
            indentation (Optional[int]): The number of spaces to use for indentation in the
            JSON output.If None, a default indentation of 2 spaces is used.

        Raises:
            OSError: If an error occurs while writing the JSON string to the file.
        """
        ind = 2 if indentation is None else indentation
        json_str = json.dumps(
            [model.model_dump() for model in point_models], indent=ind
        )

        if filename is not None:
            try:
                async with aiofiles.open(filename, mode="w", encoding="utf-8") as f:
                    await f.write(json_str)
                print(f"Output written to {filename}")
            except Exception as e:
                raise OSError("Error writing to file") from e
            return None
        return json_str
