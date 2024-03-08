"""This module contains unit tests for the PointModel class in the
coordextract.point module.
"""

from unittest.mock import MagicMock, patch

import pytest

from coordextract.models.point import PointModel


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
        (37.65815587109628, -101.45319156731206, None, "blank_mgrs"),
        (900, -101.45319156731206, "14SKG8360370719", "bad_latitude"),
        (37.65815587109628, -900, "14SKG8360370719", "bad_longitude"),
    ],
)
@patch("coordextract.conversion_utils.lat_lon_to_mgrs")
def test_create_point(
    mock_lat_lon_to_mgrs: MagicMock,
    latitude: float,
    longitude: float,
    mgrs: str,
    test_condition: str,
) -> None:
    """
    Test the build method of the PointModel class.
    """
    if test_condition == "valid":
        mock_lat_lon_to_mgrs.return_value = mgrs
        point = PointModel.build(latitude, longitude, {})
        assert point is not None
        assert point.latitude == latitude
        assert point.longitude == longitude
        assert point.mgrs == mgrs
    if test_condition == "invalid_mgrs":
        mock_lat_lon_to_mgrs.return_value = mgrs
        with pytest.raises(ValueError) as exc_info:
            PointModel.build(latitude, longitude, {})
        assert "Invalid MGRS coordinate" in str(exc_info.value)
    if test_condition == "bad_latitude":
        with pytest.raises(ValueError) as exc_info:
            PointModel.build(latitude, longitude, {})
        assert "Invalid latitude" in str(exc_info.value)
    if test_condition == "bad_longitude":
        with pytest.raises(ValueError) as exc_info:
            PointModel.build(latitude, longitude, {})
        assert "Invalid longitude" in str(exc_info.value)
    if test_condition == "blank_mgrs":
        mock_lat_lon_to_mgrs.return_value = mgrs
        point = PointModel.build(latitude, longitude, {})
        assert point is None
