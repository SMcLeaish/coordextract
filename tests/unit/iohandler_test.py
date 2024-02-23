"""This module tests the file handler module."""

from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
import pytest

# watch for Magika type stubs to be released
from coordextract.coordextract import GPXHandler, JSONHandler
from coordextract.point import PointModel


async def mock_process_gpx_to_point_models(_file_path: str) -> list[PointModel]:
    """Creates a mock call to gpx_to_point_model to create a
    PointModel."""
    mock_point = PointModel(
        gpxpoint="waypoint",
        latitude=34.12345,
        longitude=-117.12345,
        mgrs="11SPA1234567890",
    )
    return [mock_point]


@pytest.mark.asyncio
@patch("coordextract.iohandler.process_gpx_to_point_models", new_callable=AsyncMock)
async def test_gpxhandler_process_input(mock_process_gpx: MagicMock) -> None:
    """
    Test case for the `process_input` method of GPXHandler class.

    This test verifies that the `process_input` method returns an empty list when the
    `mock_process_gpx` function is called with the "test.gpx" file.

    Args:
        mock_process_gpx (MagicMock): A MagicMock object representing the `process_gpx` function.

    Returns:
        None
    """
    mock_process_gpx.return_value = []
    handler = GPXHandler(Path("test.gpx"))
    result = await handler.process_input()
    assert result == []
    mock_process_gpx.assert_awaited_once_with("test.gpx")


def test_gpxhandler_process_output_raises() -> None:
    """
    Test case to verify that GPXHandler's process_output method raises NotImplementedError.
    """
    handler = GPXHandler(Path("test.gpx"))
    with pytest.raises(NotImplementedError):
        handler.process_output([], None)


@pytest.mark.asyncio
async def test_jsonhandler_process_input_raises() -> None:
    """
    Test case to verify that process_input raises NotImplementedError when called.
    """
    handler = JSONHandler(Path("test.json"))
    with pytest.raises(NotImplementedError):
        await handler.process_input()


@patch("coordextract.iohandler.point_models_to_json")
def test_jsonhandler_process_output(mock_to_json: MagicMock) -> None:
    """
    Test case for the `process_output` method of the `JSONHandler` class.

    Args:
        mock_to_json (MagicMock): A mock object for the `to_json` function.

    Returns:
        None
    """
    point_model = PointModel(latitude=0.0, longitude=0.0, mgrs="33TWN1234567890")
    point_models = [point_model for _ in range(3)]
    handler = JSONHandler(Path("test.json"))
    handler.process_output(point_models, 4)
    mock_to_json.assert_called_once_with(point_models, "test.json", 4)


@patch("coordextract.iohandler.point_models_to_json")
def test_jsonhandler_process_output_no_file(mock_to_json: MagicMock) -> None:
    """
    Test case for the `process_output` method of the `JSONHandler` class when no file is provided.

    Args:
        mock_to_json (MagicMock): A MagicMock object for the `to_json` function.

    Returns:
        None
    """
    point_model = PointModel(latitude=0.0, longitude=0.0, mgrs="33TWN1234567890")
    point_models = [point_model for _ in range(3)]
    handler = JSONHandler(None)
    handler.process_output(point_models, 4)
    mock_to_json.assert_called_once_with(point_models, None, 4)
