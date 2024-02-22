"""Defines data models for representing geographic points in various
formats and coordinates systems."""

import math
import logging
from typing import Optional, Any
from pydantic import BaseModel, field_validator, ConfigDict
from coordextract.converters.latlon_to_mgrs import latlon_to_mgrs


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
    gpxpoint: Optional[str] = None
    latitude: float
    longitude: float
    mgrs: str

    @field_validator("latitude")
    def validate_latitude(cls, v: float) -> float:
        """Validates latitude is in a possible range.

        Returns:
        Valid latidude.
        Raises:
        Value Error.
        """
        if not -90 <= v <= 90:
            raise ValueError("Latitude must be between -90 and 90.")
        return v

    @field_validator("longitude")
    def validate_longitude(cls, v: float) -> float:
        """Validates longitude is in a possible range.

        Returns:
        Valid longitude.
        Raises:
        Value Error.
        """
        if not -180 <= v <= 180:
            raise ValueError("Longitude must be between -180 and 180.")
        return v

    @classmethod
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
        if math.isnan(latitude) or math.isnan(longitude):
            logging.warning(
                "Skipping invalid point with attributes: %s, %s", latitude, longitude
            )
            return None

        mgrs = latlon_to_mgrs(latitude, longitude)

        point_data = {
            "gpxpoint": point_type,
            "latitude": latitude,
            "longitude": longitude,
            "mgrs": mgrs,
            **additional_fields,
        }

        return cls(**point_data)
