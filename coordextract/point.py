"""Defines data models for representing geographic points in various
formats and coordinates systems."""

import math
import logging
from typing import Optional, Any
import re
from pydantic import BaseModel, field_validator, ConfigDict
from mgrs.core import MGRSError
import mgrs

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
        if PointModel.validate_latitude(v):
            return v
        return None
    @field_validator("longitude")
    def longitude_field_validator(cls, v: float) -> Optional[float]:
        """Validates longitude is in a possible range.

        Returns:
        Valid longitude.
        Raises:
        Value Error.
        """
        if PointModel.validate_longitude(v):
            return v
        return None
    @field_validator("mgrs")
    def mgrs_field_validator(cls, v: str) -> Optional[str]:
        """Validates mgrs is in a possible range.

        Returns:
        Valid mgrs.
        Raises:
        Value Error.
        """
        if PointModel.validate_mgrs(v):
            return v
        return None
    @staticmethod
    def lat_lon_to_mgrs(latitude: float, longitude: float) -> Optional[str]:
        """
        Converts latitude and longitude to MGRS (Military Grid Reference System) coordinates.

        Args:
            latitude (float): The latitude value in decimal degrees.
            longitude (float): The longitude value in decimal degrees.

        Returns:
            Optional[str]: The MGRS coordinates as a string, or None if there was an error.

        """
        try:
            m = mgrs.MGRS()
            mgrs_str = m.toMGRS(latitude, longitude)
            if PointModel.validate_mgrs(mgrs_str):
                return mgrs_str
        except MGRSError as e:
            raise e
        return None
    @staticmethod
    def mgrs_to_lat_lon(mgrs_str: str) -> Optional[tuple[float, float]]:
        """
        Converts MGRS (Military Grid Reference System) coordinates to latitude and longitude.

        Args:
            mgrs_str (str): The MGRS coordinates as a string.

        Returns:
            Optional[Tuple[float, float]]: A tuple of latitude and longitude in decimal degrees,
            or None if there was an error.
        """
        try:
            m = mgrs.MGRS()
            lat, lon = m.toLatLon(mgrs_str)
            if PointModel.validate_latitude(lat) and PointModel.validate_longitude(lon):
                return lat, lon
        except MGRSError as e:
            raise e
        return None
    @staticmethod
    def validate_latitude(latitude: float) -> bool:
        """
        Validates the latitude value.

        Args:
            latitude (float): The latitude value to be validated.

        Returns:
            bool: True if the latitude is valid, False otherwise.

        Raises:
            ValueError: If the latitude is invalid.
        """
        if math.isnan(latitude) or not -90 <= latitude <= 90:
            raise ValueError(f"Invalid latitude: {latitude}")
        return True
    @staticmethod
    def validate_longitude(longitude: float) -> bool:
        """
        Validates the longitude value.

        Args:
            longitude (float): The longitude value to be validated.

        Returns:
            bool: True if the longitude is valid, False otherwise.

        Raises:
            ValueError: If the longitude is not within the range of -180 to 180.
        """
        if math.isnan(longitude) or not -180 <= longitude <= 180:
            raise ValueError(f"Invalid longitude: {longitude}")
        return True
    @staticmethod
    def validate_mgrs(mgrs_str:str) -> bool:
        """
        Validates the MGRS coordinate.

        Args:
            mgrs (str): The MGRS coordinate to be validated.

        Returns:
            bool: True if the MGRS coordinate is valid, False otherwise.

        Raises:
            ValueError: If the MGRS coordinate is invalid.
        """
        mgrs_reg_ex = r"^\d{1,2}[^ABIOYZabioyz][A-Za-z]{2}(\d{10}|\d{8}|\d{6}|\d{4}|\d{2})$"
        if not re.match(mgrs_reg_ex, mgrs_str):
            raise ValueError('Invalid MGRS coordinate')
        return True
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
        mgrs_str = cls.lat_lon_to_mgrs(latitude, longitude)
        if mgrs_str is None:
            return None
        if 'gpxpoint' not in additional_fields:
            additional_fields['gpxpoint'] = point_type
        point_data = {
            "gpxpoint": point_type,
            "latitude": latitude,
            "longitude": longitude,
            "mgrs": mgrs_str,
            **additional_fields,
        }

        return cls(**point_data)
