"""
This module converts latitude and longitude to mgrs.
Args:
Tuple (float, float) (latitude,longitude)
Returns:
str 10 digit mgrs
Example:
latlon_to_mgrs((20.00, -105.00))
"""

__all__ = ["latlon_to_mgrs"]
import logging
from mgrs.core import MGRSError
import mgrs


def latlon_to_mgrs(latitude: float, longitude: float) -> str:
    """
    Latitude and longintude to mgrs conversion function.
    Args:
    Tuple (float, float) (latitude, logitude)
    Returns:
    mgrs_coordinates
    """
    try:
        m = mgrs.MGRS()
        mgrs_coordinate = m.toMGRS(latitude, longitude)
        return mgrs_coordinate
    except MGRSError:
        logging.exception("Error converting latitude and longitude to mgrs")
        raise
