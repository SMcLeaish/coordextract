"""This module provides utilities for converting geographic coordinates
and handling geographic data formats. It offers functionality to convert
latitude and longitude to Military Grid Reference System (MGRS)
coordinates, process input files in the GPX format adding MGRS data, and
export data to JSON format with optional indentation.

For users interested in command-line interaction, this package includes a CLI tool. 
See the README or use the `--help` option with the CLI tool for usage instructions and options.

Available Functions:
- latlon_to_mgrs(latitude: float, longitude: float) -> str:
  Converts a pair of latitude and longitude coordinates to a 10-digit MGRS string.

- inputhandler(filename: str) -> list[PointModel]:
  Processes an input file based on its MIME type. Currently supports GPX files, converting them 
  into a list of PointModel instances representing the geographic points.

- outputhandler
(point_models: list[PointModel], filename: Optional[str], indentation: Optional[int]) -> None:
  Exports a list of PointModel instances to a JSON file with optional indentation. 
  If no filename is provided, outputs to stdout.

Example Usage:
>>> from coordextract import latlon_to_mgrs, inputhandler, outputhandler
>>> mgrs_coord = latlon_to_mgrs(20.00, -105.00)
>>> points = asyncio.run(inputhandler('path/to/file.gpx'))
>>> outputhandler(points, 'output.json', 2)
"""

from .models.point import PointModel
from .converters.latlon_to_mgrs_converter import latlon_to_mgrs
from .handler import inputhandler, outputhandler, get_mimetype

__all__ = [
    "inputhandler",
    "outputhandler",
    "latlon_to_mgrs",
    "get_mimetype",
    "PointModel",
]
