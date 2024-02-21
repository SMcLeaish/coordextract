from typing import Optional
from pathlib import Path
from abc import ABC, abstractmethod
from .models.point import PointModel
from .converters.gpx_to_model import process_gpx_to_point_models
from .converters.model_to_json import point_models_to_json


class IOHandler(ABC):

    def __init__(self, filename: Optional[Path] = None):
        self.filename = filename

    @abstractmethod
    async def process_input(self):
        pass

    @abstractmethod
    def process_output(self, data, indentation: Optional[int] = None):
        pass


class GPXHandler(IOHandler):
    async def process_input(self) -> list[PointModel]:
        return await process_gpx_to_point_models(str(self.filename))

    def process_output(self, data, indentation: Optional[int] = None):
        raise NotImplementedError(
            "Only GPX input is supported, GPX output processing is not supported."
        )



class JSONHandler(IOHandler):
    async def process_input(self):
        raise NotImplementedError(
            "Only JSON output is supported, JSON input processing is not supported."
        )

    def process_output(
        self, point_models: list[PointModel], indentation: Optional[int] = None
    ) -> Optional[str]:
        if self.filename is not None:
            point_models_to_json(point_models, str(self.filename), indentation)
            return None
        return point_models_to_json(point_models, None, indentation)
