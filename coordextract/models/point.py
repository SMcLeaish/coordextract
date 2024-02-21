"""Defines data models for representing geographic points in various
formats and coordinates systems."""

import math
import logging
from pydantic import BaseModel
from coordextract.converters.latlon_to_mgrs import latlon_to_mgrs


class PointModel(BaseModel):
    """Represents a geographic point with optional name and type,
    latitude and longitude coordinates, and MGRS (Military Grid
    Reference System) notation.

    Attributes:
        name (str | None): Optional name of the point.
        gpxpoint (str | None): Optional type of the point (e.g., waypoint, trackpoint, routepoint).
        latitude (float): Latitude of the point.
        longitude (float): Longitude of the point.
        mgrs (str): MGRS notation for the geographic location of the point.
    """

    gpxpoint: str
    latitude: float
    longitude: float
    mgrs: str

    class Config:
        extra = "allow"

    @classmethod
    def create_from_gpx_data(
        cls, point_type: str, latitude: float, longitude: float, additional_fields: dict
    ):
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
