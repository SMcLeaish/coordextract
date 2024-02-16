import math
import logging
from coordextract.parsers import async_parse_gpx 
from coordextract.converters import latlon_to_mgrs 
from coordextract.models.point import PointModel

print(async_parse_gpx.__module__)
async def process_gpx_to_point_models(gpx_file_path: str) -> list[PointModel]:
    waypoints, trackpoints, routepoints = await async_parse_gpx(gpx_file_path)
    points_with_types = {
        'waypoint': waypoints,
        'trackpoint': trackpoints,
        'routepoint': routepoints,
    }
    point_models = []
    for point_type, points in points_with_types.items():
        for latitude, longitude in points:
            if math.isnan(latitude) or math.isnan(longitude):
                logging.error\
                    ("Skipping invalid point with coordinates: %s, %s", latitude, longitude)
                continue
            mgrs = latlon_to_mgrs(latitude, longitude)
            point_model = PointModel(
                name=None,
                gpxpoint=point_type,
                latitude=latitude,
                longitude=longitude,
                mgrs=mgrs
            )
            point_models.append(point_model)
    return point_models
