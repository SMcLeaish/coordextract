"""
Unit testing for mgrs conversion module.
"""
from typing import Any
from unittest.mock import patch
import pytest

# Assuming your function is in a module named `mgrs_processing`
from mgrs_processing import latlon_to_mgrs

@pytest.fixture
def mock_mgrs_success():
    """
    This function produces a properly formatted mock value 
    """
    with patch('mgrs_processing.mgrs.MGRS') as mock_mgrs:
        instance = mock_mgrs.return_value
        instance.toMGRS.return_value = b"14SKG8360370719"
        yield instance

def test_latlon_to_mgrs_success(mock_mgrs_success:  Any): 
    """
    This function tests passing mgrs_processing a properly formated mock value
    """
    latitude, longitude = 37.65815587109628, -101.45319156731206
    result = latlon_to_mgrs(latitude, longitude)
    assert result == "14SKG8360370719", "Should return the correct MGRS string for valid inputs"

@pytest.fixture
def mock_mgrs_failure():
    """
    This function produces an improperly formatted mock value 
    """
    with patch('mgrs_processing.mgrs.MGRS') as mock_mgrs:
        instance = mock_mgrs.return_value
        instance.toMGRS.side_effect = ValueError("Invalid latitude or longitude")  
        yield instance

def test_latlon_to_mgrs_failure\
    (caplog: pytest.LogCaptureFixture, mock_mgrs_failure: Any): 
    """
    This function tests passing mgrs_processinr an improperly formated mock value
    """
    result = latlon_to_mgrs(900, -900)
    assert result is None, "Should return None for invalid inputs"
    assert "Error converting latitude and longitude to mgrs" in caplog.text, \
        "Should log an error for invalid inputs"
