"""Defines data models for representing geographic points in various
formats and coordinates systems."""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, field_validator

import coordextract.conversion_utils as cu


class PointModel(BaseModel):
    """Represents a geographic point with optional name and type,
    latitude and longitude coordinates, and MGRS (Military Grid
    Reference System) notation.

    Attributes:
        latitude (float): Latitude of the point.
        longitude (float): Longitude of the point.
        mgrs (str): MGRS notation for the geographic location of the
            point.
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
        if cu.validate_latitude(v):
            return v
        raise ValueError("Invalid latitude")

    @field_validator("longitude")
    def longitude_field_validator(cls, v: float) -> Optional[float]:
        """Validates longitude is in a possible range.

        Returns:
            Valid longitude.
        Raises:
            Value Error.
        """
        if cu.validate_longitude(v):
            return v
        raise ValueError("Invalid longitude")

    @field_validator("mgrs")
    def mgrs_field_validator(cls, v: str) -> Optional[str]:
        """Validates mgrs is in a possible range.

        Returns:
            Valid mgrs.
        Raises:
            Value Error.
        """
        if cu.validate_mgrs(v):
            return v
        raise ValueError("Invalid MGRS coordinate")

    @classmethod
    def build(
        cls,
        latitude: float,
        longitude: float,
        additional_fields: dict[Any, Any],
    ) -> Optional["PointModel"]:
        """Calculates MGRS from latitude and longitude and populates the
        point data.

        Args:
            latitude (float): Latitude of the point.
            longitude (float): Longitude of the point.
            additional_fields (dict): Additional fields for the point.

        Returns:
            PointModel: A PointModel instance with the calculated MGRS
            and additional fields.
        """
        mgrs_str = cu.lat_lon_to_mgrs(latitude, longitude)
        if mgrs_str is None:
            return None
        point_data = {
            "latitude": latitude,
            "longitude": longitude,
            "mgrs": mgrs_str,
            **additional_fields,
        }

        return cls(**point_data)
