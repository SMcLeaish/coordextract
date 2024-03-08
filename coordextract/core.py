"""This module contains the implementation of the CoordExtract class and
its subclasses, which are used for input/output handling of geographic
data files.

The CoordExtract class is an abstract base class that defines the
common interface for input/output handlers. It provides methods for
processing input data and processing output data.

The GPXHandler class is a subclass of CoordExtract and provides specific
implementation for handling GPX files. It includes methods for
processing input GPX files and raising an error for output processing.
The GPXHandler class uses the GPXUtils class to process GPX files. The
GPXUtils class is a utility class that provides methods for extracting
geographic data from GPX files and converting the data to a list of
PointModel pydantic model objects, using the PointModel class defined in
the point module.

The JSONHandler class is a subclass of CoordExtract and provides
specific implementation for handling JSON files. It includes methods for
raising an error for input processing and processing output JSON files.
It uses a context parameter to determine whether to write the output to
a file, print the output to stdout, or return the output as a list of
PointModel pydantic model objects.

Note: This module requires the Magika library for file type
identification.
"""

import json
import mimetypes
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, Tuple

import aiofiles
from magika.magika import Magika  # type: ignore
from magika.types import MagikaResult  # type: ignore
from pydantic import BaseModel, FilePath

from .gpx_utils import GPXUtils
from .csv_utils import CSVUtils
from .models.point import PointModel
from .models.config import ConfigModel


class CoordExtract(ABC):
    """Abstract base class for input/output handlers."""

    def __init__(
        self,
        filepath: Optional[Path] = None,
        concurrency: bool = False,
        context: Optional[str] = None,
    ):
        """Initializes the CoordExtract with optional parameters.

        Args:
            filepath (Optional[Path]): The filepath to be processed.
                Defaults to None.
            concurrency (Optional[bool]): Flag indicating whether to
                use cpu concurrency. Defaults to False.
            context (Optional[str]): Additional context information.
                Defaults to None.
        """
        self.filename = filepath
        self.concurrency = concurrency
        self.context = context

    @abstractmethod
    async def process_input(self) -> Optional[list[PointModel]]:
        """Abstract method to process input data."""

    @abstractmethod
    async def process_output(
        self,
        point_models: list[PointModel],
        indentation: Optional[int] = None,
    ) -> Optional[str] | list[PointModel]:
        """Abstract method to process output data.

        Args:
            data: The data to be processed.
            indentation (Optional[int]): The indentation level for the
                output. Defaults to None.
        """

    @staticmethod
    async def process_coords(args: dict[str, Any], config: ConfigModel) ->\
        Optional[str] | list[PointModel]:
        """Processes a geographic data file and outputs the results to a
        specified file or stdout.

        This method serves as the core processing workflow, invoking
        input handling to parse and convert geographic data from the
        specified input file and then using output handling to
        serialize and write the data to a JSON file or stdout with
        optional indentation. It provides user feedback on the process
        success or reasons for failure.

        Args:
            input_argument (Path): The path to the input file
                containing geographic data to be processed.
            output_argument (Optional[Path]): The path to the output
                JSON file where the processed data should be saved. If
                None, the output will be printed to stdout.
            indentation (Optional[int]): The number of spaces used for
                JSON output indentation. Defaults to None.
            concurrency (Optional[bool]): Flag indicating whether to
            use concurrency. Defaults to False.
            context (Optional[str]): Runtime context information.
            Defaults to None. If set to cli, the method will print the
            output to stdout. If set to None, the method will return the
            the pydantic models.

        Returns:
            Optional[str] | list[PointModel]: The processed data as a
                JSON string or a list of PointModel objects.

        Raises:
            ValueError: If the file type is unsupported or the file type
            cannot be determined.
        """
        input_argument = args.get('input_argument')
        output_argument = args.get('output_argument', None)  
        indentation = args.get('indentation', None)
        concurrency = args.get('concurrency', False)
        context = args.get('context', None)

        input_handler = CoordExtract._factory(
            input_argument, concurrency, context
        )
        filehandler_result = await input_handler.process_input()
        if filehandler_result is not None and output_argument is not None:
            output_handler = CoordExtract._factory(
                output_argument, concurrency, context
            )
            output_handler.filename = output_argument
            await output_handler.process_output(
                filehandler_result, indentation
            )
            return None
        if filehandler_result is not None:
            output_handler = CoordExtract._factory(None, concurrency, context)
            output_str = await output_handler.process_output(
                filehandler_result, indentation
            )
            if output_str is not None:
                return output_str
        else:
            raise ValueError(
                "Error: File handler returned None. Check the input\
                 file path or filehandler implementation."
            )
        return None

    @classmethod
    def _factory(
        cls,
        filename: Optional[Path] = None,
        concurrency: bool = False,
        context: Optional[str] = None,
    ) -> "CoordExtract":
        """Factory function to create an appropriate CoordExtract based
        on the file type.

        Args:
            filename (Optional[Path]): The path to the file. Defaults to
                None.
            concurrency (Optional[bool]): Flag indicating whether to use
                concurrency. Defaults to False.
            context (Optional[str]): Additional runtime context
                information. Defaults to None.

        Returns:
            CoordExtract: An instance of the appropriate CoordExtract
                subclass.

        Raises:
            ValueError: If the file type is unsupported or the file type
                cannot be determined.
        """
        if filename is None:
            return JSONHandler(None, concurrency, context)
        mimetype, magika_result = cls._get_mimetype(filename)
        if mimetype is None or magika_result is None:
            raise ValueError(
                f"Could not determine the filetype of: {filename}"
            )
        if (
            mimetype == "application/gpx+xml"
            and magika_result.output.mime_type == "text/xml"
        ):
            return GPXHandler(filename, concurrency)
        if (
            mimetype == "text/csv"
            and magika_result.output.mime_type == "text/plain"
        ):
            return CSVHandler(filename, concurrency, context)
        if mimetype == "application/json":
            return JSONHandler(filename, concurrency, context)
        raise ValueError(f"Unsupported file type for {filename}")

    @staticmethod
    def _get_mimetype(
        filename: Path,
    ) -> Tuple[Optional[str], Optional[MagikaResult]]:
        """Get the mimetype of a file using the filename extension and
        Magika library.

        Args:
            filename (Path): The path to the file.

        Returns:
            Tuple[Optional[str], Optional[MagikaResult]]: A tuple
                containing the mimetype and the MagikaResult object.
        """
        mimetypes.add_type("application/gpx+xml", ".gpx")
        mimetypes.add_type("application/json", ".json")
        mimetypes.add_type("text/csv", ".csv")
        mimetypes.add_type("application/vnd.google-earth.kml+xml", ".kml")
        m = Magika()
        mimetype, _ = mimetypes.guess_type(filename)
        magika_result = m.identify_path(filename)
        return mimetype, magika_result


class GPXHandler(CoordExtract):
    """Input/output handler for GPX files."""

    def __init__(
        self, filename: Path, concurrency: bool, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(filename, concurrency, *args, **kwargs)
        self.gpx_utils = GPXUtils(concurrency=self.concurrency)

    async def process_input(self) -> list[PointModel]:
        """Processes the input GPX file and returns a list of PointModel
        objects. If the concurrency is set to tru, the processing is
        done concurrently using concurrent.futures.ProcessPoolExecutor.

        Returns:
            Optional[list[PointModel]]: The list of PointModel objects
                extracted from the GPX file, or None if the processing
                fails.
        """
        return await self.gpx_utils.process_gpx(self.filename)

    async def process_output(
        self, point_models: list[PointModel], indentation: Optional[int] = None
    ) -> None:
        """Raises a NotImplementedError as GPX output processing is not
        supported.

        Args:
            point_models (list[PointModel]): The data to be processed.
            indentation (Optional[int]): The indentation level for the
            output. Defaults to None.

        Raises:
            NotImplementedError: GPX output processing is not supported.
        """
        raise NotImplementedError("Only JSON output is supported.")

class CSVHandler(CoordExtract):
    """Input/output handler for CSV files."""
    def __init__(
        self, filename: Path, concurrency: bool, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(filename, concurrency, *args, **kwargs)
        self.gpx_utils = CSVUtils(concurrency=self.concurrency)

    async def process_input(self) -> list[PointModel]:
        """Raises a NotImplementedError as CSV input processing is not
        supported.

        Raises:
            NotImplementedError: CSV input processing is not supported.
        """
        return await self.csv_utils.process_csv(self.filename)

    async def process_output(
        self, point_models: list[PointModel], indentation: Optional[int] = None
    ) -> None:
        """Raises a NotImplementedError as CSV output processing is not
        supported.

        Args:
            point_models (list[PointModel]): The data to be processed.
            indentation (Optional[int]): The indentation level for the
            output. Defaults to None.

        Raises:
            NotImplementedError: CSV output processing is not supported.
        """
        raise NotImplementedError("Only JSON output is supported.")

class JSONHandler(CoordExtract):
    """Input/output handler for JSON files."""

    async def process_input(self) -> None:
        """Raises a NotImplementedError as JSON input processing is not
        supported.

        Raises:
            NotImplementedError: JSON input processing is not supported.
        """
        raise NotImplementedError("Only GPX input is supported.")

    async def process_output(
        self, point_models: list[PointModel], indentation: Optional[int] = None
    ) -> Optional[str] | list[PointModel]:
        """Processes the output data and returns the JSON representation
        of the PointModel objects, or the PointModel objects as a list.

        Args:
            point_models (list[PointModel]): The list of PointModel
                objects to be processed.
            indentation (Optional[int]): The indentation level for the
                output. Defaults to None.

        Returns:
            Optional[str]: The JSON representation of the PointModel
                objects. If the filename is provided, the JSON string is
                written to the file and None is returned. If the context
                is set to cli, the JSON string is printed to stdout and
                None is returned. If the context is set to None, the
                PointModel objects are returned as a list. The
                PointModel objects are pydantic models and can be
                serialized by fastapi.
        """
        if self.filename is not None:
            await self._point_models_to_json(
                point_models, self.filename, indentation
            )
            return None
        if self.context is None:
            return point_models
        return await self._point_models_to_json(
            point_models, None, indentation
        )

    async def _point_models_to_json(
        self,
        point_models: list[PointModel],
        filename: Optional[Path] = None,
        indentation: Optional[int] = None,
    ) -> Optional[str]:
        """Serializes a list of PointModel instances to JSON format and
        writes to a file or prints to stdout.

        This function converts a list of PointModel instances into a
        JSON-formatted string with the specified indentation level.
        If a filename is provided, the JSON string is written to the
        specified file. Otherwise, the JSON string is printed to stdout.

        Args:
            point_models (list[PointModel]): A list of PointModel
                instances to be serialized.
            filename (Optional[str]): The path to the output file where
                the JSON string should be saved. If None, the JSON
                string is printed to stdout instead.
            indentation (Optional[int]): The number of spaces to use for
                indentation in the JSON output.If None, a default
                indentation of 2 spaces is used.

        Raises:
            OSError: If an error occurs while writing the JSON string to
                the file.
        """
        json_str = json.dumps(
            [model.model_dump() for model in point_models], indent=indentation
        )

        if filename is not None:
            try:
                async with aiofiles.open(
                    filename, mode="w", encoding="utf-8"
                ) as f:
                    await f.write(json_str)
                print(f"Output written to {filename}")
            except Exception as e:
                raise OSError("Error writing to file") from e
            return None
        return json_str
