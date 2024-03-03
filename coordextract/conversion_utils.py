"""
This module contains utility functions for converting between and 
validating MGRS (Military Grid Reference System) and latitude and 
longitude coordinates.
"""

import math
import re
from typing import Optional

import mgrs
from mgrs.core import MGRSError


def mgrs_to_lat_lon(mgrs_str: str) -> Optional[tuple[float, float]]:
    """Converts MGRS (Military Grid Reference System) coordinates to
    latitude and longitude.

    Args:
        mgrs_str (str): The MGRS coordinates as a string.

    Returns:
        Optional[Tuple[float, float]]: A tuple of latitude and longitude
        in decimal degrees, or None if there was an error.
    Raises:
        MGRSError: If there is an error converting the MGRS to latitude
            and longitude.
    """
    try:
        if not validate_mgrs(mgrs_str):
            raise ValueError("Invalid MGRS string")
        m = mgrs.MGRS()
        lat, lon = m.toLatLon(mgrs_str)
        if not validate_latitude(lat):
            raise ValueError("Invalid latitude")
        if not validate_longitude(lon):
            raise ValueError("Invalid longitude")
        return lat, lon
    except (MGRSError, ValueError) as e:
        raise MGRSError(
            "Error converting MGRS to latitude and longitude"
        ) from e


def lat_lon_to_mgrs(latitude: float, longitude: float) -> Optional[str]:
    """Converts latitude and longitude to MGRS (Military Grid Reference
    System) coordinates.

    Args:
        latitude (float): The latitude value in decimal degrees.
            longitude (float): The longitude value in decimal degrees.

    Returns:
        Optional[str]: The MGRS coordinates as a string, or None if
            there was an error.
    Raises:
        MGRSError: If there is an error converting the latitude and
            longitude to MGRS.
    """
    try:
        if not validate_latitude(latitude):
            raise ValueError("Invalid latitude")
        if not validate_longitude(longitude):
            raise ValueError("Invalid longitude")
        m = mgrs.MGRS()
        mgrs_str = m.toMGRS(latitude, longitude)
        if not validate_mgrs(mgrs_str):
            raise ValueError("Invalid MGRS string returned by mgrs.toMGRS")
        return mgrs_str
    except (MGRSError, ValueError) as e:
        raise MGRSError(
            "Error converting latitude and longitude to MGRS"
        ) from e


def validate_latitude(latitude: float) -> bool:
    """Validates the latitude value.

    Args:
        latitude (float): The latitude value to be validated.

    Returns:
        bool: True if the latitude is valid, False otherwise.
    """
    if math.isnan(latitude) or not -90 <= latitude <= 90:
        return False
    return True


def validate_longitude(longitude: float) -> bool:
    """Validates the longitude value.

    Args:
        longitude (float): The longitude value to be validated.

    Returns:
        bool: True if the longitude is valid, False otherwise.
    """
    if math.isnan(longitude) or not -180 <= longitude <= 180:
        return False
    return True


def validate_mgrs(mgrs_str: str) -> bool:
    """
    Validates the MGRS string against the regular expression pattern.
    Args:
        mgrs_str (str): The MGRS string to be validated.
    Returns:
        bool: True if the MGRS string is valid, False otherwise.
    """
    mgrs_reg_ex = (
        r"^\d{1,2}[^ABIOYZabioyz][A-Za-z]{2}(\d{10}|\d{8}|\d{6}|\d{4}|\d{2})$"
    )
    if re.match(mgrs_reg_ex, mgrs_str):
        return True
    return False
