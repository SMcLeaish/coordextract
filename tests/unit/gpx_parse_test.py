import pytest
from pathlib import Path
from mgrs_processing.parsers.gpx_parse import async_parse_gpx

@pytest.mark.asyncio
async def test_async_parse_gpx_empty_file(caplog):
    data_file = Path(__file__).parent.parent / 'data' / 'empty.gpx'
    waypoints, trackpoints, routepoints = await async_parse_gpx(str(data_file))
    assert waypoints == []
    assert trackpoints == []
    assert routepoints == []
    assert "GPX file is empty or unreadable" in caplog.text
