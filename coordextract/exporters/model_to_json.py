import json
import logging
from typing import Optional
from coordextract.models.point import PointModel


def point_models_to_json(
    point_models: list[PointModel],
    filename: Optional[str] = None,
    indentation: Optional[int] = None,
) -> None:
    ind = 2 if indentation is None else indentation
    json_str = json.dumps([model.model_dump() for model in point_models], indent=ind)

    if filename:
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"Output written to {filename}")
        except OSError:
            logging.exception("Error writing to file")
    else:
        print(json_str)
