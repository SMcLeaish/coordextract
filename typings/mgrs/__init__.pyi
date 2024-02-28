from typing import Any, Tuple

class MGRS:
    def toMGRS(self, latitude: float, longitude: float, *args: Any) -> str: ...
    def toLatLon(
        self, MGRS: str, inDegrees: bool = True
    ) -> Tuple[float, float]: ...
