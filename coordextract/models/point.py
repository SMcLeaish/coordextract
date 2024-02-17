"""
Defines data models for representing geographic points in various formats and coordinates systems.
"""

from pydantic import BaseModel


class PointModel(BaseModel):
    """
    Represents a geographic point with optional name and type, latitude and longitude coordinates,
    and MGRS (Military Grid Reference System) notation.

    Attributes:
        name (str | None): Optional name of the point.
        gpxpoint (str | None): Optional type of the point (e.g., waypoint, trackpoint, routepoint).
        latitude (float): Latitude of the point.
        longitude (float): Longitude of the point.
        mgrs (str): MGRS notation for the geographic location of the point.
    """

    name: str | None = None
    gpxpoint: str | None = None
    latitude: float
    longitude: float
    mgrs: str
