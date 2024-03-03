"""Unit testing for mgrs conversion module."""

from unittest.mock import patch

import pytest
from mgrs.core import MGRSError
from pytest import approx

from coordextract.conversion_utils import lat_lon_to_mgrs, mgrs_to_lat_lon


@pytest.mark.parametrize(
    "latitude, longitude, mgrs, test_condition",
    [
        (37.65815587109628, -101.45319156731206, "14SKG8360370719", "valid"),
        (
            37.65815587109628,
            -101.45319156731206,
            "00AAB1234567890",
            "invalid_mgrs",
        ),
        (900, -101.45319156731206, "14SKG8360370719", "bad_latitude"),
        (37.65815587109628, -900, "14SKG8360370719", "bad_longitude"),
    ],
)
def test_conversion_functions(
    latitude: float,
    longitude: float,
    mgrs: str,
    test_condition: str,
) -> None:
    """Test the lat_lon_to_mgrs and mgrs_to_lat_lon functions."""
    if test_condition == "valid":
        with patch(
            "coordextract.conversion_utils.validate_mgrs", return_value=True
        ):
            mgrs_result = lat_lon_to_mgrs(latitude, longitude)
            assert mgrs_result == mgrs
            lat_lon_result = mgrs_to_lat_lon(mgrs)
            if lat_lon_result is not None:
                lat_result, lon_result = lat_lon_result
                assert approx(lat_result) == approx(latitude)
                assert approx(lon_result) == approx(longitude)
    elif test_condition == "invalid_mgrs":
        with patch(
            "coordextract.conversion_utils.validate_mgrs", return_value=False
        ), pytest.raises(MGRSError) as excinfo:
            lat_lon_to_mgrs(latitude, longitude)
        assert "Invalid MGRS string returned by mgrs.toMGRS" in str(
            excinfo.value.__cause__
        )
        with pytest.raises(MGRSError) as excinfo:
            mgrs_to_lat_lon(mgrs)
        assert "Invalid MGRS string" in str(excinfo.value.__cause__)
    else:
        with pytest.raises(MGRSError) as excinfo:
            lat_lon_to_mgrs(latitude, longitude)
        if test_condition == "bad_latitude":
            assert "Invalid latitude" in str(excinfo.value.__cause__)
            with patch(
                "coordextract.conversion_utils.validate_latitude",
                return_value=False,
            ), pytest.raises(MGRSError) as excinfo:
                mgrs_to_lat_lon(mgrs)
            assert "Invalid latitude" in str(excinfo.value.__cause__)
        elif test_condition == "bad_longitude":
            assert "Invalid longitude" in str(excinfo.value.__cause__)
            with patch(
                "coordextract.conversion_utils.validate_longitude",
                return_value=False,
            ), pytest.raises(MGRSError) as excinfo:
                mgrs_to_lat_lon(mgrs)
            assert "Invalid longitude" in str(excinfo.value.__cause__)
