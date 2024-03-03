"""Tests for GPX point model processing in the `coordextract` package,
covering parsing, MGRS conversion, and error handling."""

from pathlib import Path
from typing import Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from lxml import etree

from coordextract.gpx_utils import GPXUtils
from coordextract.point import PointModel


@pytest.fixture
def mock_point_model() -> MagicMock:
    """Return a mock PointModel object."""
    return MagicMock(spec=PointModel)


########################################################################
# GPXUtils.process_gpx tests
########################################################################


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "gpx_file_path, concurrency, raises_error,\
expected_result",
    [
        (Path("/valid/no_concurrent_path.gpx"), False, False, [MagicMock()]),
        (Path("/valid/path.gpx"), True, False, [MagicMock()]),
        (None, True, True, None),
        (Path("/invalid/path.gpx"), True, True, None),
        (None, False, True, None),
    ],
)
async def test_process_gpx(
    mock_point_model: MagicMock,
    gpx_file_path: Optional[Path],
    concurrency: bool,
    raises_error: bool,
    expected_result: Optional[list[MagicMock]],
) -> None:
    """Test the process_gpx method of the GPXUtils class."""
    gpx_utils = GPXUtils(concurrency=concurrency)
    if expected_result is not None:
        expected_result = [mock_point_model()]
    with patch.object(
        GPXUtils, "parse_gpx", new=MagicMock(return_value=expected_result)
    ) as mock_parse_gpx, patch(
        "aiofiles.open", create=True
    ) as mock_aiofiles_open, patch(
        "asyncio.get_running_loop"
    ) as mock_get_running_loop:

        mock_file = AsyncMock()
        mock_file.read = AsyncMock(return_value="mock xml data")
        mock_aiofiles_open.return_value = AsyncMock(
            __aenter__=AsyncMock(return_value=mock_file),
            __aexit__=AsyncMock(return_value=None),
        )
        if concurrency:
            mock_loop = AsyncMock()
            mock_get_running_loop.return_value = mock_loop
            mock_loop.run_in_executor = AsyncMock(return_value=expected_result)
        if raises_error and gpx_file_path is not None:
            mock_aiofiles_open.side_effect = OSError()
            with pytest.raises(OSError) as exc_info:
                await gpx_utils.process_gpx(gpx_file_path)
                assert "Error accessing file" in str(exc_info.value)
        elif raises_error and gpx_file_path is None:
            with pytest.raises(ValueError) as exc_info:
                await gpx_utils.process_gpx(gpx_file_path)
                assert "No file path provided" in str(exc_info.value)
        else:
            result = await gpx_utils.process_gpx(gpx_file_path)
            assert result == expected_result
            mock_aiofiles_open.assert_called_once_with(gpx_file_path, "rb")
            if concurrency:
                mock_get_running_loop.assert_called_once()
                mock_loop.run_in_executor.assert_called()
            else:
                mock_parse_gpx.assert_called_once()


########################################################################
# GPXUtils.parse_gpx tests
########################################################################


@pytest.mark.parametrize(
    "test_condition, raises_error,\
expected_exception_message",
    [
        ("valid_gpx_data", False, None),
        ("empty_gpx_data", True, "GPX data is empty or unreadable"),
        ("invalid_gpx_data", True, "invalid XML"),
    ],
)
def test_parse_gpx(
    test_condition: str, raises_error: bool, expected_exception_message: str
) -> None:
    """Test the parse_gpx method of the GPXUtils class."""
    valid_xml: bytes = b"""<?xml version="1.0" encoding="UTF-8"?>
    <gpx version="1.1" creator="exampleCreator"\
    xmlns="http://www.topografix.com/GPX/1/1">
    <wpt lat="10.0" lon="-20.0">
    <name>Test Waypoint</name>
    <ele>123.45</ele>
    <time>2021-01-01T00:00:00Z</time>
    </wpt>
    </gpx>"""
    invalid_xml: bytes = b"""<?xml version="9000" encoding="UTF-8"?>
    <gpx version="1.1" creator="exampleCreator"\
    xmlns="http://www.topografix.com/GPX/1/1">
    <wpt lat="10.0" lon="-20.0">
    <name>Test Waypoint</name>
    <ele>123.45</ele>
    <time>2021-01-01T00:00:00Z</time>
    </wpt>
    """

    if raises_error and test_condition == "empty_gpx_data":
        xml_data = b""
        with pytest.raises(ValueError) as exc_info:
            GPXUtils.parse_gpx(False, xml_data)
        assert expected_exception_message in str(exc_info.value)
    elif raises_error and test_condition == "invalid_gpx_data":
        xml_data = invalid_xml
        with pytest.raises(ValueError) as exc_info:
            GPXUtils.parse_gpx(False, xml_data)
        assert expected_exception_message in str(exc_info.value)
    else:
        xml_data = valid_xml
        result = GPXUtils.parse_gpx(False, xml_data)
        assert result is not None and len(result) == 1
        assert all(isinstance(item, PointModel) for item in result)


########################################################################
# GPXUtils._build_point tests
########################################################################
Parsedgpx = dict[str, list[tuple[float, float, dict[str, str | Any]] | None]]


@pytest.mark.parametrize(
    "points_with_types, concurrent, expected_call_count",
    [
        ({"wpt": [(10.0, -20.0, {"name": "Test Waypoint"})]}, False, 1),
    ],
)
def test_build_gpx_point_models(
    points_with_types: Parsedgpx,
    concurrent: bool,
    expected_call_count: int,
    mock_point_model: MagicMock,
) -> None:
    """Test the _build_gpx_point_models method of the GPXUtils class."""
    with patch(
        "coordextract.point.PointModel.build", return_value=mock_point_model()
    ) as mock_build:
        # pylint: disable=protected-access
        result = GPXUtils._build_gpx_point_models(
            points_with_types, concurrent
        )
        # pylint: enable=protected-access
        assert mock_build.call_count == expected_call_count
        assert result == [mock_point_model()]


########################################################################
# GPXUtils._parse_point tests
########################################################################


@pytest.mark.parametrize(
    "xml_input, expected_output, raises_error",
    [
        (
            '<point lat="40.6892" lon="-74.0445">\
            <name>Liberty Island</name></point>',
            (40.6892, -74.0445, {"name": "Liberty Island"}),
            False,
        ),
        (
            '<point lon="-74.0445"><name>Liberty Island</name></point>',
            None,
            False,
        ),
        (
            '<point lat="40.6892"><name>Liberty Island</name></point>',
            None,
            False,
        ),
        ('<point lat="invalid" lon="74.0445"></point>', None, True),
    ],
)
def test_parse_point(
    xml_input: str,
    expected_output: tuple[float | str, float, dict[str, str]] | None,
    raises_error: bool,
) -> None:
    """Test the parse_point function."""
    point = etree.fromstring(xml_input)
    # pylint: disable=protected-access
    if raises_error:
        with pytest.raises(ValueError) as excinfo:
            GPXUtils._parse_point(point)
        assert "Invalid coordinate value encountered" in str(excinfo.value)
    else:
        assert GPXUtils._parse_point(point) == expected_output
    # pylint: enable=protected-access
