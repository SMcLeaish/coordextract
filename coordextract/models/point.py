from pydantic import BaseModel

class PointModel(BaseModel):
    name: str | None = None
    gpxpoint: str | None = None
    latitude: float
    longitude: float
    mgrs: str
