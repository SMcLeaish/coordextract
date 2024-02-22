"""
This module provides a factory function to create an appropriate IOHandler based on the file type.
It also includes a function to get the mimetype of a file using the filename extension and Magika 
library.

The supported file types are:
- GPX (application/gpx+xml)
- JSON (application/json)

If the file type is unsupported or the file type cannot be determined, a ValueError is raised.

The module exports the following symbols:
- MagikaResult: A type representing the result of the Magika library identification.
- IOHandler: The base class for all IOHandlers.
- GPXHandler: An IOHandler subclass for GPX files.
- JSONHandler: An IOHandler subclass for JSON files.
"""

from typing import Optional, Tuple
from pathlib import Path
import mimetypes
from magika.magika import Magika  # type: ignore
from magika.types import MagikaResult  # type: ignore
from .iohandler import IOHandler, GPXHandler, JSONHandler


def get_mimetype(filename: Path) -> Tuple[Optional[str], Optional[MagikaResult]]:
    """
    Get the mimetype of a file using the filename extension and Magika library.

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


def handler_factory(filename: Optional[Path] = None) -> IOHandler:
    """
    Factory function to create an appropriate IOHandler based on the file type.

    Args:
        filename (Optional[Path]): The path to the file. Defaults to None.

    Returns:
        IOHandler: An instance of the appropriate IOHandler subclass.

    Raises:
        ValueError: If the file type is unsupported or the file type cannot be determined.

    """
    if filename is None:
        return JSONHandler()
    mimetype, magika_result = get_mimetype(filename)
    if mimetype is None or magika_result is None:
        raise ValueError(f"Could not determine the filetype of: {filename}")
    if (
        mimetype == "application/gpx+xml"
        and magika_result.output.mime_type == "text/xml"
    ):
        return GPXHandler(filename)
    if mimetype == "application/json":
        return JSONHandler(filename)
    raise ValueError(f"Unsupported file type for {filename}")


__all__ = ["MagikaResult", "IOHandler", "GPXHandler", "JSONHandler"]
