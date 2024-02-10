"""Pytest unit tests for gpx_parser.
"""
from pathlib import Path
import pytest
from mgrs_processing.parsers.gpx_parse import async_parse_gpx

@pytest.mark.asyncio
async def test_async_parse_gpx_empty_file(caplog):
    """Passes empty gpx file from tests/data. 
       Args:
       empty_file: empty .gpx file
       Returns:
       Return three empty lists and an error
    """
    empty_file = Path(__file__).parent.parent / 'data' / 'empty.gpx'
    waypoints, trackpoints, routepoints = await async_parse_gpx(str(empty_file))
    assert waypoints == []
    assert trackpoints == []
    assert routepoints == []
    assert "GPX file is empty or unreadable" in caplog.text
