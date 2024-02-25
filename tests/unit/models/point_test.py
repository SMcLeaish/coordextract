"""This module contains unit tests for the PointModel class in the
coordextract.models.point module.

The PointModel class represents a point with latitude and longitude
coordinates, along with additional fields.
The unit tests in this module cover various scenarios for creating
PointModel objects and validating the latitude and longitude values.

The module includes the following test cases:
- test_create_from_gpx_data_success: Tests the create_from_gpx_data
method of the PointModel class with valid point data.
- test_create_from_gpx_data_invalid: Tests the create_from_gpx_data
method of the PointModel class with invalid point data.
- test_create_from_gpx_data_includes_dynamic_fields: Tests that the
create_from_gpx_data method includes dynamic fields in the created
point model object.
- test_latitude_validation: Tests the validation of the latitude value.
- test_longitude_validation: Tests the validation of the longitude value.

The module also includes fixture functions for generating valid and
invalid point data, as well as a mock function for latlon_to_mgrs.

Note: This module requires the pytest, pydantic, and pytest_mock libraries to run the tests.
"""

from typing import Any
from unittest.mock import MagicMock, patch
import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture
from coordextract.point import PointModel


@pytest.fixture
def valid_point_data() -> dict[str, Any]:
    """Returns a dictionary representing valid point data.

    Returns:
        dict[str, Any]: A dictionary containing the following keys:
            - 'point_type': The type of the point (e.g., 'waypoint').
            - 'latitude': The latitude coordinate of the point.
            - 'longitude': The longitude coordinate of the point.
            - 'additional_fields': Additional fields associated with the point.
    """
    return {
        "point_type": "waypoint",
        "latitude": 34.12345,
        "longitude": -117.12345,
        "additional_fields": {"name": "Test Point"},
    }


@pytest.fixture
def invalid_point_data() -> dict[str, Any]:
    """Returns a dictionary representing invalid point data.

    The dictionary contains the following keys:
    - 'point_type': The type of the point (e.g., 'waypoint').
    - 'latitude': The latitude of the point (set to NaN).
    - 'longitude': The longitude of the point (set to NaN).
    - 'additional_fields': Additional fields associated with the point (an empty dictionary).

    Returns:
    A dictionary representing invalid point data.
    """
    return {
        "point_type": "waypoint",
        "latitude": float("nan"),
        "longitude": float("nan"),
        "additional_fields": {},
    }


@patch("coordextract.models.point.latlon_to_mgrs")
def test_create_from_gpx_data_success(
    mock_latlon_to_mgrs: MagicMock, valid_point_data: dict[str, Any]
) -> None:
    """Test case for the create_from_gpx_data method of the PointModel
    class.

    Args:
        mock_latlon_to_mgrs: A mock object for the latlon_to_mgrs function.
        valid_point_data: A dictionary containing valid point data.

    Returns:
        None
    """
    mock_latlon_to_mgrs.return_value = "31U BT 00000 00000"
    point = PointModel.create_from_gpx_data(**valid_point_data)
    assert point is not None
    assert point.gpxpoint == valid_point_data["point_type"]
    assert point.latitude == valid_point_data["latitude"]
    assert point.longitude == valid_point_data["longitude"]
    assert point.mgrs == "31U BT 00000 00000"


def test_create_from_gpx_data_invalid(invalid_point_data: dict[str, Any]) -> None:
    """Test case for the create_from_gpx_data method of the PointModel
    class when invalid point data is provided.

    Args:
        invalid_point_data (dict[str, Any]): Invalid point data to
        be used for creating the PointModel.

    Returns:
        None
    """
    point = PointModel.create_from_gpx_data(**invalid_point_data)
    assert point is None


@pytest.mark.asyncio
async def test_create_from_gpx_data_includes_dynamic_fields() -> None:
    """Test case to verify that the create_from_gpx_data method of
    PointModel includes dynamic fields in the created point model
    object."""
    additional_fields = {"name": "Dynamic Name", "another_field": "Another Value"}
    point_model = PointModel.create_from_gpx_data(
        "waypoint", 34.12345, -117.12345, additional_fields
    )
    assert getattr(point_model, "name", None) == "Dynamic Name"
    assert getattr(point_model, "another_field", None) == "Another Value"


@pytest.fixture
def mock_latlon_to_mgrs(mocker: MockerFixture) -> None:
    """Mocks the latlon_to_mgrs function and returns a predefined MGRS
    value.

    Args:
        mocker (MockerFixture): The mocker fixture object.

    Returns:
        None
    """
    mocker.patch(
        "coordextract.models.point.latlon_to_mgrs", return_value="33TWN1234567890"
    )


@pytest.mark.parametrize(
    "latitude, is_valid",
    [
        (90.0, True),
        (-90.0, True),
        (0.0, True),
        (45.12345, True),
        (-45.12345, True),
        (90.1, False),
        (-90.1, False),
        (None, False),
    ],
)
def test_latitude_validation(latitude: float, is_valid: bool) -> None:
    """Test the validation of latitude value.

    Args:
        latitude (Optional[float]): The latitude value to be tested.
        is_valid (bool): Flag indicating whether the latitude value is expected to be valid or not.

    Raises:
        ValidationError: If the latitude value is not a float.

    Returns:
        None
    """
    if not isinstance(latitude, float):
        with pytest.raises(ValidationError):
            PointModel(latitude=latitude, longitude=0, mgrs="33TWN1234567890")
    else:
        try:
            PointModel(latitude=latitude, longitude=0, mgrs="33TWN1234567890")
            assert is_valid
        except ValidationError:
            assert not is_valid


@pytest.mark.parametrize(
    "longitude, is_valid",
    [
        (180, True),
        (-180, True),
        (0, True),
        (90.12345, True),
        (-90.12345, True),
        (180.1, False),
        (-180.1, False),
        (None, False),
    ],
)
def test_longitude_validation(
    longitude: float, is_valid: bool, mock_latlon_to_mgrs: None
) -> None:
    """Test the validation of the longitude parameter in the PointModel
    class.

    Args:
        longitude (Optional[float]): The longitude value to be tested.
        is_valid (bool): Indicates whether the longitude value is expected to be valid or not.
        mock_latlon_to_mgrs (None): A mock object for the latlon_to_mgrs function.

    Raises:
        AssertionError: If the instantiation of PointModel with a valid longitude value
        raises a ValidationError.
        ValidationError: If the instantiation of PointModel with an invalid longitude value
        does not raise a ValidationError.
    """
    if is_valid:
        try:
            point = PointModel(latitude=0, longitude=longitude, mgrs="33TWN1234567890")
            assert point.longitude == longitude
        except ValidationError:
            pytest.fail("Unexpected ValidationError for a valid longitude value")
    else:
        with pytest.raises(ValidationError):
            PointModel(latitude=0, longitude=longitude, mgrs="33TWN1234567890")
