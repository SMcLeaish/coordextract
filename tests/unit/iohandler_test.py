"""This module tests the file handler module."""

from unittest.mock import patch, MagicMock, AsyncMock
from typing import Generator, cast
from pathlib import Path
import pytest
# watch for Magika type stubs to be released
from coordextract.iohandler import GPXHandler, JSONHandler
from coordextract.models.point import PointModel


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
@patch('coordextract.iohandler.process_gpx_to_point_models', new_callable=AsyncMock)
async def test_gpxhandler_process_input(mock_process_gpx):
    mock_process_gpx.return_value = []  
    handler = GPXHandler(Path("test.gpx"))
    result = await handler.process_input()
    assert result == []
    mock_process_gpx.assert_awaited_once_with("test.gpx")

def test_gpxhandler_process_output_raises():
    handler = GPXHandler(Path("test.gpx"))
    with pytest.raises(NotImplementedError):
        handler.process_output([], None)

@pytest.mark.asyncio
async def test_jsonhandler_process_input_raises():
    handler = JSONHandler(Path("test.json"))
    with pytest.raises(NotImplementedError):
        await handler.process_input()

@patch('coordextract.iohandler.point_models_to_json')
def test_jsonhandler_process_output(mock_to_json):
    point_models = [MagicMock(spec=PointModel) for _ in range(3)]
    point_models = cast(list[PointModel], point_models)
    handler = JSONHandler(Path("test.json"))
    handler.process_output(point_models, 4)
    mock_to_json.assert_called_once_with(point_models, "test.json", 4)

@patch('coordextract.iohandler.point_models_to_json')
def test_jsonhandler_process_output_no_file(mock_to_json):
    point_models = [MagicMock(spec=PointModel) for _ in range(3)]
    point_models = cast(list[PointModel], point_models)
    handler = JSONHandler(None)
    handler.process_output(point_models, 4)
    mock_to_json.assert_called_once_with(point_models, None, 4)