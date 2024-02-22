"""Tests for GPX point model processing in the `coordextract` package,
covering parsing, MGRS conversion, and error handling."""

from unittest.mock import AsyncMock, patch
import pytest
from coordextract.converters.gpx_to_model import process_gpx_to_point_models


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "return_value, expected_length",
    [
        (([(25.0, 3.0, {})], [], []), 1),
        (([(30.0, 5.0, {})], [(35.0, 10.0, {})], []), 2),
        (([], [], []), 0),
    ],
)
@patch("coordextract.converters.gpx_to_model.async_parse_gpx", new_callable=AsyncMock)
async def test_process_gpx_to_point_models_with_data(
    mock_async_parse_gpx: AsyncMock,
    return_value: list[tuple[float, float, dict]],
    expected_length: int,
) -> None:
    """Tests the processing of GPX data to PointModels, ensuring correct
    handling of different return values.

    This test verifies that `process_gpx_to_point_models` correctly
    processes various sets of GPX data, resulting in the expected number
    of PointModels.

    Args:
    - mock_latlon_to_mgrs: Mocked function converting latitude and longitude to MGRS.
    - mock_async_parse_gpx: Mocked asynchronous function for parsing GPX data.
    - mock_logging_error: Mocked logging for capturing error logs.
    - return_value: Mock return value for the async GPX parsing function, simulating
    different parsing outcomes.
    - expected_length: The expected number of PointModels generated from the input GPX data.
    """

    mock_async_parse_gpx.return_value = return_value
    result = await process_gpx_to_point_models("dummy_path.gpx")
    mock_async_parse_gpx.assert_called_once()
    assert (
        len(result) == expected_length
    ), f"Expected {expected_length} PointModel(s) to be created"
