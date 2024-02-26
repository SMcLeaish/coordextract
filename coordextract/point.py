"""Defines data models for representing geographic points in various
formats and coordinates systems."""

from typing import Optional, Any
from pydantic import BaseModel, field_validator, ConfigDict
import coordextract.conversion_utils as cu


class PointModel(BaseModel):
    """Represents a geographic point with optional name and type,
    latitude and longitude coordinates, and MGRS (Military Grid
    Reference System) notation.

    Attributes:
        gpxpoint (str | None): Optional type of the point (e.g., waypoint, trackpoint, routepoint).
        latitude (float): Latitude of the point.
        longitude (float): Longitude of the point.
        mgrs (str): MGRS notation for the geographic location of the point.
        Accepts a dictionary of extra fields.
    """

    model_config = ConfigDict(extra="allow")
    latitude: float
    longitude: float
    mgrs: str

    @field_validator("latitude")
    def latitude_field_validator(cls, v: float) -> Optional[float]:
        """Validates latitude is in a possible range.

        Returns:
        Valid latidude.
        Raises:
        Value Error.
        """
        try:
            if cu.validate_latitude(v):
                return v
        except ValueError:
            raise ValueError("Invalid latitude") from None
        return None

    @field_validator("longitude")
    def longitude_field_validator(cls, v: float) -> Optional[float]:
        """Validates longitude is in a possible range.

        Returns:
        Valid longitude.
        Raises:
        Value Error.
        """
        try:
            if cu.validate_longitude(v):
                return v
        except ValueError:
            raise ValueError("Invalid longitude") from None
        return None

    @field_validator("mgrs")
    def mgrs_field_validator(cls, v: str) -> Optional[str]:
        """Validates mgrs is in a possible range.

        Returns:
        Valid mgrs.
        Raises:
        Value Error.
        """
        try:
            if cu.validate_mgrs(v):
                return v
        except ValueError:
            raise ValueError("Invalid MGRS coordinate") from None
        return None

    @classmethod
    # this should be define from gpx_data and create should be independent
    def create_from_gpx_data(
        cls,
        point_type: str,
        latitude: float,
        longitude: float,
        additional_fields: dict[Any, Any],
    ) -> Optional["PointModel"]:
        """Calculates MGRS from latitude and longitude and populates the
        point data.

        This class method creates an instance of the PointModel with given latitude,
        longitude, point type, and merges any additional fields provided. If the
        latitude or longitude is not a number (NaN), the method logs a warning and
        returns None.

        Args:
            point_type (str): The type of the geographic point (e.g., 'waypoint', 'trackpoint',
            'routepoint').
            latitude (float): The latitude of the geographic point in decimal degrees.
            longitude (float): The longitude of the geographic point in decimal degrees.
            additional_fields (dict): Additional data to be merged into the point model.

        Returns:
            PointModel: An instance of `PointModel` populated with the provided data
                        and the calculated MGRS string.

        Raises:
            ValueError: If `latlon_to_mgrs` cannot process the provided latitude and
                        longitude to generate an MGRS string.
        """
        mgrs_str = cu.lat_lon_to_mgrs(latitude, longitude)
        if mgrs_str is None:
            return None
        if "gpxpoint" not in additional_fields:
            additional_fields["gpxpoint"] = point_type
        point_data = {
            "gpxpoint": point_type,
            "latitude": latitude,
            "longitude": longitude,
            "mgrs": mgrs_str,
            **additional_fields,
        }

        return cls(**point_data)
