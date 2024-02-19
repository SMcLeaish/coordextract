"""Pytest unit tests for gpx_parser."""

from pathlib import Path
import pytest
from coordextract.parsers import async_parse_gpx


@pytest.mark.asyncio
async def test_async_parse_gpx_empty_file(caplog: pytest.LogCaptureFixture) -> None:
    """Passes empty gpx file from tests/data.

    Args:
    empty_file: empty .gpx file
    Returns:
    Return three empty lists and an error
    """
    empty_file = Path(__file__).parent.parent / "data" / "empty.gpx"
    waypoints, trackpoints, routepoints = await async_parse_gpx(str(empty_file))
    assert waypoints == []
    assert trackpoints == []
    assert routepoints == []
    assert "GPX file is empty or unreadable" in caplog.text


@pytest.mark.asyncio
async def test_async_parse_gpx_valid_file() -> None:
    """Passes empty gpx file from tests/data.

    Args:
    valid_file: valid test .gpx file
    Returns:
    Returns data in waypoints, an empty list in trackpoints, data in  routepoints
    """
    empty_file = Path(__file__).parent.parent / "data" / "fells_loop.gpx"
    waypoints, trackpoints, routepoints = await async_parse_gpx(str(empty_file))
    assert waypoints != []
    assert trackpoints == []
    assert routepoints != []
