"""
This module contains the definition of input/output handlers for GPX and JSON files.

The module includes an abstract base class `IOHandler` that defines the 
common interface for input/output handlers.
It also provides concrete implementations for GPX files (`GPXHandler`) 
and JSON files (`JSONHandler`).

The `IOHandler` class is an abstract base class that cannot be instantiated directly.
It defines two abstract methods: `process_input()` and `process_output()`, 
which need to be implemented by subclasses.

The `GPXHandler` class is a subclass of `IOHandler` and provides implementation 
for processing GPX files.
It overrides the `process_input()` method to extract `PointModel` objects from the GPX file.
The `process_output()` method is also overridden to raise a `NotImplementedError` 
as GPX output processing is not supported.

The `JSONHandler` class is another subclass of `IOHandler` and provides 
implementation for processing JSON files.
It raises a `NotImplementedError` in the `process_input()` method as 
JSON input processing is not supported.
The `process_output()` method is implemented to convert `PointModel` objects to JSON representation.

The `PointModel` class is imported from the `.models.point` module.
The `process_gpx_to_point_models()` function is imported from the `.converters.gpx_to_model` module.
The `point_models_to_json()` function is imported from the `.converters.model_to_json` module.
"""

from typing import Optional
from pathlib import Path
from abc import ABC, abstractmethod
from .models.point import PointModel
from .converters.gpx_to_model import process_gpx_to_point_models
from .converters.model_to_json import point_models_to_json


class IOHandler(ABC):
    """
    Abstract base class for input/output handlers.
    """

    def __init__(self, filename: Optional[Path] = None):
        """
        Initializes the IOHandler with an optional filename.

        Args:
            filename (Optional[Path]): The filename to be processed. Defaults to None.
        """
        self.filename = filename

    @abstractmethod
    async def process_input(self) -> Optional[list[PointModel]]:
        """
        Abstract method to process input data.
        """

    @abstractmethod
    def process_output(
        self, point_models: list[PointModel], indentation: Optional[int] = None
    ) -> Optional[str]:
        """
        Abstract method to process output data.

        Args:
            data: The data to be processed.
            indentation (Optional[int]): The indentation level for the output. Defaults to None.
        """


class GPXHandler(IOHandler):
    """
    Input/output handler for GPX files.
    """

    async def process_input(self) -> list[PointModel]:
        """
        Processes the input GPX file and returns a list of PointModel objects.

        Returns:
            list[PointModel]: The list of PointModel objects extracted from the GPX file.
        """
        return await process_gpx_to_point_models(str(self.filename))

    def process_output(
        self, point_models: list[PointModel], indentation: Optional[int] = None
    ) -> None:
        """
        Raises a NotImplementedError as GPX output processing is not supported.

        Args:
            point_models (list[PointModel]): The data to be processed.
            indentation (Optional[int]): The indentation level for the output. Defaults to None.

        Raises:
            NotImplementedError: GPX output processing is not supported.
        """
        raise NotImplementedError(
            "Only GPX input is supported, GPX output processing is not supported."
        )


class JSONHandler(IOHandler):
    """
    Input/output handler for JSON files.
    """

    async def process_input(self) -> None:
        """
        Raises a NotImplementedError as JSON input processing is not supported.

        Raises:
            NotImplementedError: JSON input processing is not supported.
        """
        raise NotImplementedError(
            "Only JSON output is supported, JSON input processing is not supported."
        )

    def process_output(
        self, point_models: list[PointModel], indentation: Optional[int] = None
    ) -> Optional[str]:
        """
        Processes the output data and returns the JSON representation of the PointModel objects.

        Args:
            point_models (list[PointModel]): The list of PointModel objects to be processed.
            indentation (Optional[int]): The indentation level for the output. Defaults to None.

        Returns:
            Optional[str]: The JSON representation of the PointModel objects.
        """
        if self.filename is not None:
            point_models_to_json(point_models, str(self.filename), indentation)
            return None
        return point_models_to_json(point_models, None, indentation)
