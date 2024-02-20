"""This module contains tests for the GPX parsing functionality.

It includes unit tests for validating the parsing of GPX point elements
and the asynchronous parsing of GPX files, covering various scenarios
like valid inputs, error handling, and unsupported GPX versions.
"""

from unittest.mock import MagicMock, patch
from typing import Any, Tuple
import math
import logging
import aiofiles
import pytest
from lxml import etree
from coordextract.parsers.gpx_parse import async_parse_gpx
from coordextract.parsers.gpx_parse import parse_point


@pytest.fixture
def mock_gpx_point() -> etree._Element:
    """Creates a mock GPX point element with valid latitude and
    longitude attributes.

    Returns:
    An lxml _Element instance representing a GPX point.
    """
    point = etree.Element("point")
    point.set("lat", "10.0")
    point.set("lon", "-20.0")
    return point


# pylint: disable=redefined-outer-name
def test_parse_point_valid(mock_gpx_point: etree._Element) -> None:
    """Tests if the parse_point function correctly parses valid GPX
    point elements.

    Args:
    mock_gpx_point: A fixture that provides a mock GPX point element with valid coordinates.
    """
    assert parse_point(mock_gpx_point) == (
        10.0,
        -20.0,
    ), "Should correctly parse valid GPX point"


@pytest.fixture
def mock_invalid_gpx_point() -> etree._Element:
    """Creates a mock GPX point element with invalid latitude and
    longitude attributes.

    Returns:
    An lxml _Element instance representing a GPX point.
    """
    point = etree.Element("point")
    point.set("lat", "invalid")
    point.set("lon", "invalid")
    return point


def test_parse_point_invalid(
    mock_invalid_gpx_point: etree._Element, caplog: pytest.LogCaptureFixture
) -> None:
    """Tests the parse_point function with invalid latitude and
    longitude attributes to ensure it logs an exception as expected.

    Args:
    mock_invalid_gpx_point: A fixture that provides a mock invalid GPX point element
    """
    with caplog.at_level(logging.ERROR):
        result = parse_point(mock_invalid_gpx_point)
        assert result == (
            math.nan,
            math.nan,
        ), "Should return NaN for invalid coordinates"
        assert "Invalid coordinate value encountered." in caplog.text


@pytest.mark.asyncio
async def test_async_parse_valid_gpx_with_mock() -> None:
    """Uses aiofiles and MagicMock object to mock a file read with valid
    xml data."""
    mock_file_content: bytes = b"""<?xml version="1.0" encoding="UTF-8"?>
    <gpx version="1.1" creator="exampleCreator" xmlns="http://www.topografix.com/GPX/1/1">
    <wpt lat="10.0" lon="-20.0">
    <name>Test Waypoint</name>
    <ele>123.45</ele>
    <time>2021-01-01T00:00:00Z</time>
    </wpt>
    </gpx>"""

    async def mock_async_read(
        *_args: Tuple[Any, ...], **_kwargs: dict[str, Any]
    ) -> bytes:
        return mock_file_content

    mock_file_obj: MagicMock = MagicMock()
    mock_file_obj.read = mock_async_read
    aiofiles.threadpool.wrap.register(MagicMock)(  # type: ignore
        lambda *args, **kwargs: mock_file_obj
    )

    with patch(
        "aiofiles.threadpool.sync_open",
        return_value=MagicMock(return_value=mock_file_obj),
    ):
        waypoints, trackpoints, routepoints = await async_parse_gpx("dummy_path.gpx")
    assert isinstance(waypoints, list), "Should be a list of waypoint tuples"
    assert isinstance(trackpoints, list), "Should be a list of trackpoint tuples"
    assert isinstance(routepoints, list), "Should be a list of routepoint tuples"
    assert waypoints != [], "Should not be empty"
    assert trackpoints == [], "Should be empty"
    assert routepoints == [], "Should be empty"


@pytest.mark.asyncio
async def test_async_parse_empty_gpx_with_mock(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Uses aiofiles and MagicMock object to mock a file read with empty
    data."""
    mock_file_content: bytes = b""

    async def mock_async_read(
        *_args: Tuple[Any, ...], **_kwargs: dict[str, Any]
    ) -> bytes:
        return mock_file_content

    mock_file_obj: MagicMock = MagicMock()
    mock_file_obj.read = mock_async_read
    aiofiles.threadpool.wrap.register(MagicMock)(  # type: ignore
        lambda *args, **kwargs: mock_file_obj
    )

    with patch(
        "aiofiles.threadpool.sync_open",
        return_value=MagicMock(return_value=mock_file_obj),
    ):
        waypoints, trackpoints, routepoints = await async_parse_gpx("dummy_path.gpx")
    assert isinstance(waypoints, list), "Should be a list of waypoint tuples"
    assert isinstance(trackpoints, list), "Should be a list of trackpoint tuples"
    assert isinstance(routepoints, list), "Should be a list of routepoint tuples"
    assert waypoints == [], "Should be empty"
    assert trackpoints == [], "Should be empty"
    assert routepoints == [], "Should be empty"
    assert "GPX file is empty or unreadable" in caplog.text, "Should return an OS error"


@pytest.mark.asyncio
async def test_async_parse_invalid_gpx_data_with_mock(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Uses aiofiles and MagicMock object to mock a file read with gpx
    syntax error."""
    mock_file_content: bytes = b"""<?xml version="9000" encoding="UTF-8"?>
    <gpx version="1.1" creator="exampleCreator" xmlns="http://www.topografix.com/GPX/1/1">
    <wpt lat="10.0" lon="-20.0">
    <name>Test Waypoint</name>
    <ele>123.45</ele>
    <time>2021-01-01T00:00:00Z</time>
    </wpt>
    """

    async def mock_async_read(
        *_args: Tuple[Any, ...], **_kwargs: dict[str, Any]
    ) -> bytes:
        return mock_file_content

    mock_file_obj: MagicMock = MagicMock()
    mock_file_obj.read = mock_async_read
    aiofiles.threadpool.wrap.register(MagicMock)(  # type: ignore
        lambda *args, **kwargs: mock_file_obj
    )

    with patch(
        "aiofiles.threadpool.sync_open",
        return_value=MagicMock(return_value=mock_file_obj),
    ):
        waypoints, trackpoints, routepoints = await async_parse_gpx("dummy_path.gpx")
    assert isinstance(waypoints, list), "Should be a list of waypoint tuples"
    assert isinstance(trackpoints, list), "Should be a list of trackpoint tuples"
    assert isinstance(routepoints, list), "Should be a list of routepoint tuples"
    assert waypoints == [], "Should be empty"
    assert trackpoints == [], "Should be empty"
    assert routepoints == [], "Should be empty"
    assert (
        "XML syntax error in the file." in caplog.text
    ), "Should return a syntax error"


@pytest.mark.asyncio
async def test_async_parse_gpx_raises_os_error_with_mock(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Simulates an OSError on file read."""
    with patch.object(
        aiofiles, "open", side_effect=OSError("Simulated file read error")
    ):
        result = await async_parse_gpx("path/to/nonexistent/file.gpx")
        assert result == ([], [], [])
        assert (
            "Error opening or reading file" in caplog.text
        ), "Should return a file io error"
