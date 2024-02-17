import mimetypes
from typing import Optional
from coordextract.models.point import PointModel
from coordextract.factory import process_gpx_to_point_models
from coordextract.exporters import point_models_to_json


def get_mimetype(filename: str) -> str | None:
    mimetype, _ = mimetypes.guess_type(filename)
    return mimetype


async def filehandler(filename) -> list[PointModel]:
    mimetype = get_mimetype(filename)
    if mimetype == "application/gpx+xml":
        return await process_gpx_to_point_models(filename)
    raise ValueError(f"Unknown filetype: {filename}")


def outputhandler(
    point_models: list[PointModel], filename: str, indentation: Optional[int]
) -> None:
    mimetype = get_mimetype(filename)
    if mimetype == "application/json":
        point_models_to_json(point_models, filename, indentation)
    else:
        raise ValueError(f"Unsupported output file type for: {filename}")
