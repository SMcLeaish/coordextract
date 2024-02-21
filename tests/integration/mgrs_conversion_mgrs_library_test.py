"""This module tests the mgrs_conversion functionality with relation to
the mgrs library."""

import pytest
from mgrs.core import MGRSError
from coordextract.converters.latlon_to_mgrs_converter import latlon_to_mgrs


def test_latlon_to_mgrs_with_valid_data() -> None:
    """Tests latlon_to_mgrs with known values produced by the
    library."""
    assert (
        latlon_to_mgrs(37.65815587109628, -101.45319156731206) == "14SKG8360370719"
    ), "Should return the correct MGRS"


def test_latlon_to_mgrs_with_invalid_latlon(caplog: pytest.LogCaptureFixture) -> None:
    """Tests latlon_to_mgrs with values outside valid latitude and
    longitude."""
    with pytest.raises(MGRSError):
        latlon_to_mgrs(900, -900)
    assert (
        "Error converting latitude and longitude to mgrs" in caplog.text
    ), "Should return none and a conversion error"
