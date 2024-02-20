import mimetypes
from typing import Optional, Tuple
from pathlib import Path
from magika.magika import Magika  # type: ignore
from magika.types import MagikaResult  # type: ignore
from .models.point import PointModel
from .factory.gpx_model_builder import process_gpx_to_point_models
from .exporters.model_to_json import point_models_to_json

class IOHandler:
    def __init__(self, filename: Optional[Path]):
        self.filename = filename

    def get_mimetype(self) -> Tuple[Optional[str], Optional[MagikaResult]]:
        m = Magika()
        if self.filename is None:
            return None, None
        mimetype, _ = mimetypes.guess_type(str(self.filename))
        magika_result = m.identify_path(self.filename)
        return mimetype, magika_result

    async def process_input(self) -> list[PointModel]:
        mimetype, magika_result = self.get_mimetype()
        if mimetype is None or magika_result is None:
            raise ValueError(f"Could not determine the filetype of: {self.filename}")
        if mimetype == "application/gpx+xml" and magika_result.output.mime_type == "text/xml":
            return await process_gpx_to_point_models(str(self.filename))
        raise ValueError(f"Unsupported filetype: {mimetype} for file: {self.filename}.")

    def process_output(self, point_models: list[PointModel], indentation: Optional[int] = None) -> Optional[str]:
        if self.filename:
            mimetype, _ = self.get_mimetype()
            if mimetype == "application/json":
                point_models_to_json(point_models, str(self.filename), indentation)
                return None
            else:
                raise ValueError(f"Unsupported output file type: {mimetype}")
        else:
            return point_models_to_json(point_models, None, indentation)
