"""This module provides functionality for exporting geographic data,
represented as PointModel instances, to JSON format. It supports
serialization of data with customizable indentation levels and the
ability to write the output directly to a file or standard output
(stdout).

Functions:
- point_models_to_json: Serializes a list of PointModel instances into JSON, writing to a file or
  stdout.
- get_mimetype: Determines the MIME type of a given file, aiding in the processing of input files.

The module emphasizes ease of use, flexibility, and error resilience, making it suitable for
applications hat require the processing, serialization, and output of geographic data in a
structured format.

Example Usage:
from coordextract.exporters import point_models_to_json
from coordextract.models.point import PointModel

# Assuming a list of PointModel instances
points = [PointModel(...), PointModel(...)]

# Serialize and print to stdout
point_models_to_json(points)

# Serialize and write to a file with custom indentation
point_models_to_json(points, filename='output.json', indentation=4)
"""

import json
import logging
from typing import Optional
from coordextract.models.point import PointModel


def point_models_to_json(
    point_models: list[PointModel],
    filename: Optional[str] = None,
    indentation: Optional[int] = None,
) -> None:
    """Serializes a list of PointModel instances to JSON format and
    writes to a file or prints to stdout.

    This function converts a list of PointModel instances into a JSON-formatted string with the
    specified indentation level. If a filename is provided, the JSON string is written to the
    specified file. Otherwise, the JSON string is printed to stdout.

    Args:
        point_models (list[PointModel]): A list of PointModel instances to be serialized.
        filename (Optional[str]): The path to the output file where the JSON string should be saved.
                                   If None, the JSON string is printed to stdout instead.
        indentation (Optional[int]): The number of spaces to use for indentation in the JSON output.
                                      If None, a default indentation of 2 spaces is used.

    Raises:
        OSError: If an error occurs while writing the JSON string to the file.
    """
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
