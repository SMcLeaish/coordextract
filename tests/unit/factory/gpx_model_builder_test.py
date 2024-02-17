"""Tests for GPX point model processing in the `coordextract` package,
covering parsing, MGRS conversion, and error handling."""

import math
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from coordextract.factory.gpx_model_builder import process_gpx_to_point_models


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "return_value, expected_length",
    [
        (([(25.0, 3.0)], [], []), 1),
        (([(30.0, 5.0)], [(35.0, 10.0)], []), 2),
        (([], [], []), 0),
    ],
)
@patch("coordextract.factory.gpx_model_builder.async_parse_gpx", new_callable=AsyncMock)
@patch("coordextract.factory.gpx_model_builder.latlon_to_mgrs", new_callable=MagicMock)
async def test_process_gpx_to_point_models_with_data(
    mock_latlon_to_mgrs,
    mock_async_parse_gpx,
    return_value: list[tuple[float, float]],
    expected_length: list[tuple[float, float]],
):
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
    mock_latlon_to_mgrs.return_value = "19TCG266309977"
    result = await process_gpx_to_point_models("dummy_path.gpx")
    mock_async_parse_gpx.assert_called_once()
    assert (
        len(result) == expected_length
    ), f"Expected {expected_length} PointModel(s) to be created"


@pytest.mark.asyncio
@patch("logging.error")
@patch("coordextract.factory.gpx_model_builder.async_parse_gpx", new_callable=AsyncMock)
@patch("coordextract.factory.gpx_model_builder.latlon_to_mgrs", new_callable=MagicMock)
async def test_process_gpx_to_point_models_with_nan(
    mock_latlon_to_mgrs, mock_async_parse_gpx, mock_logging_error
):
    """Ensures PointModels are created correctly when encountering NaN
    values in GPX data.

    Args:
    - mock_latlon_to_mgrs (MagicMock): Mock for MGRS conversion.
    - mock_async_parse_gpx (AsyncMock): Mock for parsing GPX data, including NaNs.
    - mock_logging_error: Mock for error logging verification.
    """

    mock_async_parse_gpx.return_value = ([(math.nan, math.nan)], [(25.0, 12.0)], [])
    mock_latlon_to_mgrs.return_value = "19TCG266309977"
    result = await process_gpx_to_point_models("dummy_path.gpx")
    mock_logging_error.assert_called_once()
    mock_async_parse_gpx.assert_called_once()
    assert len(result) == 1, "Expected 1 PointModel(s) to be created"
