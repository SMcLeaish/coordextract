from unittest.mock import patch, AsyncMock
import pytest
from coordextract.factory.gpx_model_builder import process_gpx_to_point_models

@pytest.mark.asyncio
async def test_process_gpx_to_point_models_with_data():
    with patch('coordextract.factory.gpx_model_builder.async_parse_gpx', new_callable=AsyncMock, return_value=([(25.0, 3.0)], [], [])) as mock_async_parse_gpx:
        result = await process_gpx_to_point_models("dummy_path.gpx")
        mock_async_parse_gpx.assert_called_once()
        assert len(result) == 1, "Expected one PointModel to be created"
