"""
This module contains tests for the GPX parsing functionality.
It includes unit tests for validating the parsing of GPX point elements
and the asynchronous parsing of GPX files, covering various scenarios
like valid inputs, error handling, and unsupported GPX versions.
"""

import aiofiles
import pytest
from unittest.mock import MagicMock, patch
from lxml import etree
from mgrs_processing.parsers.gpx_parse import async_parse_gpx, parse_point

#class AsyncMockContextManager(MagicMock):
#    def __init__(self, *args, read_data=None, **kwargs):
#        super().__init__(*args, **kwargs)
#        self._read_data = read_data
#
#    async def __aenter__(self):
#        return self
#
#    async def __aexit__(self, exc_type, exc_val, exc_tb):
#        pass
#
#    async def read(self):
#        return self._read_data

@pytest.fixture
def mock_gpx_point() -> etree._Element:
    """
    Creates a mock GPX point element with valid latitude and longitude attributes.
    
    Returns:
        An lxml _Element instance representing a GPX point.
    """
    point = etree.Element("point")
    point.set("lat", "10.0")
    point.set("lon", "-20.0")
    return point
# pylint: disable=redefined-outer-name
def test_parse_point_valid(mock_gpx_point: etree._Element) -> None:
    """
    Tests if the parse_point function correctly parses valid GPX point elements.
    
    Args:
        mock_gpx_point: A fixture that provides a mock GPX point element with valid coordinates.
    """
    assert parse_point(mock_gpx_point) == (10.0, -20.0), "Should correctly parse valid GPX point"

def test_parse_point_invalid() -> None:
    """
    Tests the parse_point function with invalid latitude and longitude attributes
    to ensure it returns None as expected.
    """
    point = etree.Element("point")
    point.set("lat", "invalid")
    point.set("lon", "invalid")
    assert parse_point(point) is None, "Should return None for invalid coordinates"

@pytest.mark.asyncio
async def test_async_parse_gpx_with_mock():
    mock_file_content = b"""<?xml version="1.0" encoding="UTF-8"?>
    <gpx version="1.1" creator="exampleCreator" xmlns="http://www.topografix.com/GPX/1/1">
    <wpt lat="10.0" lon="-20.0">
    <name>Test Waypoint</name>
    <ele>123.45</ele>
    <time>2021-01-01T00:00:00Z</time>
    </wpt>
    </gpx>"""

    async def mock_async_read(*args, **kwargs):
        return mock_file_content

    mock_file_obj = MagicMock()
    mock_file_obj.read = mock_async_read
    aiofiles.threadpool.wrap.register(MagicMock)(
        lambda *args, **kwargs: mock_file_obj
    )

    with patch('aiofiles.threadpool.sync_open', return_value=MagicMock(return_value=mock_file_obj)):
        waypoints, trackpoints, routepoints = await async_parse_gpx("dummy_path.gpx")
    assert waypoints != [] 
    assert trackpoints == []
    assert routepoints == []