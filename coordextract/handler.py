"""This module provides functionality for handling geographic data
conversions and output processing. It includes utilities for determining
file MIME types, processing GPX files to extract geographic points, and
exporting these points to JSON format with optional indentation. The
module currently supports input files in GPX format and outputs data in
JSON format.

Functions:
- get_mimetype: Determines the MIME type of a given file based on its extension.
- inputhandler: Asynchronously processes an input file, converting it to a list of PointModel
  instances.
- outputhandler: Exports PointModel data to a JSON file or prints to stdout, with optional
  indentation.
"""

import mimetypes
from typing import Tuple, Optional
from pathlib import Path

# watch for Magika type stubs to be released
from magika.magika import Magika  # type: ignore
from magika.types import MagikaResult  # type: ignore
from .models.point import PointModel
from .factory.gpx_model_builder import process_gpx_to_point_models
from .exporters.model_to_json import point_models_to_json


def get_mimetype(filename: Path) -> Tuple[Optional[str], Optional[MagikaResult]]:
    """Determines the MIME type of a file based on its filename
    extension and Magika.

    Args:
        filename (Path): The path of the file to analyze.

    Returns:
        Tuple[Optional[str], Optional[MagikaResult]]: The determined MIME type as a string, or None
        if the type could not be determined, and the MagikaResult or None.
    """
    m = Magika()
    mimetype, _ = mimetypes.guess_type(str(filename))
    magika_result = m.identify_path(filename)

    return mimetype, magika_result


async def inputhandler(filename: Path) -> list[PointModel]:
    """Asynchronously processes an input file to convert it into a list
    of PointModel instances.

    This function supports processing of GPX files. It raises an error if the file type is
    unsupported or cannot be determined.

    Args:
        filename (str): The path to the input file.

    Returns:
        list[PointModel]: A list of PointModel instances extracted from the input file.

    Raises:
        ValueError: If the file type is unsupported or cannot be determined.
    """
    mimetype, magika_result = get_mimetype(filename)
    if mimetype is None or magika_result is None:
        raise ValueError(f"Could not determine the filetype of: {filename}")
    if (
        mimetype == "application/gpx+xml"
        and magika_result.output.mime_type == "text/xml"
    ):
        return await process_gpx_to_point_models(str(filename))
    raise ValueError(f"Unsupported filetype: {mimetype} for file: {filename}. \n ")


def outputhandler(
    point_models: list[PointModel], filename: Optional[Path], indentation: Optional[int]
) -> None:
    """Exports a list of PointModel instances to a JSON file with
    specified indentation, or prints to stdout if no filename is
    provided.

    This function supports outputting data in JSON format. If the specified output file type is
    not 'application/json', it raises an error.

    Args:
        point_models (list[PointModel]): The PointModel instances to export.
        filename (Optional[str]): The name of the output file. If None, output is printed to stdout.
        indentation (Optional[int]): The indentation level for the JSON output. Defaults to None,
        resulting in a default indentation.

    Raises:
        ValueError: If the output file type is unsupported.
    """
    if filename:
        mimetype, _ = get_mimetype(filename)
        if mimetype == "application/json":
            point_models_to_json(point_models, str(filename), indentation)
        else:
            raise ValueError(f"Unsupported output file type: {mimetype}")
    else:
        point_models_to_json(point_models, None, indentation)
