import math
from typing import Optional
import re
import mgrs
from mgrs.core import MGRSError


def mgrs_to_lat_lon(mgrs_str: str) -> Optional[tuple[float, float]]:
    """Converts MGRS (Military Grid Reference System) coordinates to
    latitude and longitude.

    Args:
        mgrs_str (str): The MGRS coordinates as a string.

    Returns:
        Optional[Tuple[float, float]]: A tuple of latitude and longitude in decimal degrees,
        or None if there was an error.
    """
    try:
        m = mgrs.MGRS()
        lat, lon = m.toLatLon(mgrs_str)
        if validate_latitude(lat) and validate_longitude(lon):
            return lat, lon
    except MGRSError as e:
        raise e
    return None


def lat_lon_to_mgrs(latitude: float, longitude: float) -> Optional[str]:
    """Converts latitude and longitude to MGRS (Military Grid Reference
    System) coordinates.

    Args:
        latitude (float): The latitude value in decimal degrees.
        longitude (float): The longitude value in decimal degrees.

    Returns:
        Optional[str]: The MGRS coordinates as a string, or None if there was an error.
    """
    try:
        m = mgrs.MGRS()
        mgrs_str = m.toMGRS(latitude, longitude)
        if validate_mgrs(mgrs_str):
            return mgrs_str
    except MGRSError as e:
        raise e
    return None


def validate_latitude(latitude: float) -> bool:
    """Validates the latitude value.

    Args:
        latitude (float): The latitude value to be validated.

    Returns:
        bool: True if the latitude is valid, False otherwise.

    Raises:
        ValueError: If the latitude is invalid.
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

    Raises:
        ValueError: If the longitude is not within the range of -180 to 180.
    """
    if math.isnan(longitude) or not -180 <= longitude <= 180:
        return False
    return True


def validate_mgrs(mgrs_str: str) -> bool:
    """Validates the MGRS coordinate.

    Args:
        mgrs (str): The MGRS coordinate to be validated.

    Returns:
        bool: True if the MGRS coordinate is valid, False otherwise.

    Raises:
        ValueError: If the MGRS coordinate is invalid.
    """
    mgrs_reg_ex = (
        r"^\d{1,2}[^ABIOYZabioyz][A-Za-z]{2}(\d{10}|\d{8}|\d{6}|\d{4}|\d{2})$"
    )
    if re.match(mgrs_reg_ex, mgrs_str):
        return True
    return False
