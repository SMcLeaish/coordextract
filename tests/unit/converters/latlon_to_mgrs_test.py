"""Unit testing for mgrs conversion module."""

from typing import Generator
from unittest.mock import patch, MagicMock
from mgrs.core import MGRSError
import pytest
from coordextract.converters.latlon_to_mgrs import latlon_to_mgrs


@pytest.fixture
def mock_mgrs_success() -> Generator[MagicMock, None, None]:
    """This function produces a properly formatted mock value."""
    with patch("mgrs.MGRS") as mock_mgrs:
        instance = mock_mgrs.return_value
        instance.toMGRS.return_value = "14SKG8360370719"
        yield instance


# pylint: disable=redefined-outer-name
def test_latlon_to_mgrs_success(mock_mgrs_success: MagicMock) -> None:
    """This function tests passing mgrs_processing a properly formated
    mock value."""
    latitude, longitude = 37.65815587109628, -101.45319156731206
    result = latlon_to_mgrs(latitude, longitude)
    assert (
        result == "14SKG8360370719"
    ), "Should return the correct MGRS string for valid inputs"
    mock_mgrs_success.toMGRS.assert_called_once_with(
        37.65815587109628, -101.45319156731206
    )


@pytest.fixture
def mock_mgrs_failure() -> Generator[MagicMock, None, None]:
    """This fixture mocks the MGRS class from the 'mgrs' library to
    raise an MGRSError for invalid inputs."""
    with patch("mgrs.MGRS") as mock_mgrs:
        instance = mock_mgrs.return_value
        instance.toMGRS.side_effect = MGRSError(
            "Invalid latitude or longitude"
        )
        yield instance


# pylint: disable=redefined-outer-name
def test_latlon_to_mgrs_failure(
    caplog: pytest.LogCaptureFixture, mock_mgrs_failure: MagicMock
) -> None:
    """Tests passing latlon_to_mgrs an improperly formatted mock
    value."""
    with pytest.raises(MGRSError):
        latlon_to_mgrs(900, -900)

    assert (
        "Error converting latitude and longitude to mgrs" in caplog.text
    ), "Should log an error for invalid inputs"
    mock_mgrs_failure.toMGRS.assert_called_once_with(900, -900)
