from typing import Optional, Tuple
from pathlib import Path
import mimetypes
from magika.magika import Magika  # type: ignore
from magika.types import MagikaResult  # type: ignore
from .iohandler import IOHandler, GPXHandler, JSONHandler


def get_mimetype(filename: Path) -> Tuple[Optional[str], Optional[MagikaResult]]:
    m = Magika()
    if filename is None:
        return None, None
    mimetype, _ = mimetypes.guess_type(str(filename))
    magika_result = m.identify_path(filename)
    return mimetype, magika_result


def handler_factory(filename: Optional[Path] = None) -> IOHandler:
    if filename is None:
        return JSONHandler()
    else:
        mimetype, magika_result = get_mimetype(filename)
    if mimetype is None or magika_result is None:
        raise ValueError(f"Could not determine the filetype of: {filename}")
    if (
        mimetype == "application/gpx+xml"
        and magika_result.output.mime_type == "text/xml"
    ):
        return GPXHandler(filename)
    elif mimetype == "application/json":
        return JSONHandler(filename)
    else:
        raise ValueError(f"Unsupported file type for {filename}")
