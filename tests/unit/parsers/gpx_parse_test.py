"""This module contains tests for the GPX parsing functionality.

It includes unit tests for validating the parsing of GPX point elements
and the asynchronous parsing of GPX files, covering various scenarios
like valid inputs, error handling, and unsupported GPX versions.
"""

from unittest.mock import MagicMock, patch
from typing import Any, Tuple
import aiofiles
import pytest
from lxml import etree
from coordextract.parsers.gpx_parse import async_parse_gpx
from coordextract.parsers.gpx_parse import parse_point


@pytest.mark.parametrize(
    "xml_input,expected_output",
    [
        (
            '<point lat="40.6892" lon="-74.0445"><name>Liberty Island</name></point>',
            (40.6892, -74.0445, {"name": "Liberty Island"}),
        ),
        ('<point lon="-74.0445"><name>Liberty Island</name></point>', None),
        ('<point lat="40.6892"><name>Liberty Island</name></point>', None),
    ],
)
def test_parse_point(
    xml_input: str, expected_output: tuple[float, float, dict[str, str]] | None
) -> None:
    """Test the parse_point function.

    Args:
        xml_input (str): The XML input for parsing.
        expected_output (tuple[float, float, dict[str, str]] | None): The expected output of the
        parse_point function.

    Returns:
        None
    """
    point = etree.fromstring(xml_input)
    assert parse_point(point) == expected_output


def test_parse_point_invalid_coordinate() -> None:
    """Test case to verify the behavior of parse_point function when an
    invalid coordinate value is encountered."""
    xml_input = '<point lat="invalid" lon="74.0445"></point>'
    point = etree.fromstring(xml_input)
    with pytest.raises(ValueError) as excinfo:
        parse_point(point)
    assert "Invalid coordinate value encountered" in str(excinfo.value)


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
async def test_async_parse_empty_gpx_with_mock() -> None:
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
        with pytest.raises(ValueError) as excinfo:
            await async_parse_gpx("dummy_path.gpx")
    assert "GPX file is empty or unreadable" in str(excinfo.value)


@pytest.mark.asyncio
async def test_async_parse_invalid_gpx_data_with_mock() -> None:
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
        with pytest.raises(ValueError) as excinfo:
            await async_parse_gpx("dummy_path.gpx")
    assert "GPX file contains invalid XML: String not closed expecting" in str(
        excinfo.value
    )


@pytest.mark.asyncio
async def test_async_parse_gpx_raises_os_error_with_mock(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Simulates an OSError on file read."""
    with patch.object(
        aiofiles, "open", side_effect=OSError("Simulated file read error")
    ):
        with pytest.raises(OSError) as excinfo:
            await async_parse_gpx("path/to/nonexistent/file.gpx")
        assert (
            "Error accessing file at path/to/nonexistent/file.gpx: Simulated file read error"
            in str(excinfo.value)
        )
