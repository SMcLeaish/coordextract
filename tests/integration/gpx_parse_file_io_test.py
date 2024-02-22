"""Pytest unit tests for gpx_parser."""

from pathlib import Path
import pytest
from coordextract.parsers.gpx_parse import async_parse_gpx


@pytest.mark.asyncio
async def test_async_parse_gpx_empty_file() -> None:
    """Test that parsing an empty GPX file raises a ValueError.

    Args:
    empty_file: empty .gpx file
    Raises:
    Value Error
    """
    empty_file = Path(__file__).parent.parent / "data" / "empty.gpx"

    with pytest.raises(ValueError) as exc_info:
        await async_parse_gpx(str(empty_file))

    assert "GPX file is empty or unreadable" in str(exc_info.value)


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
