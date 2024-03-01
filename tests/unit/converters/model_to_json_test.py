"""This module contains unit tests for the `point_models_to_json`
function in the `coordextract.converters.model_to_json` module."""

from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from coordextract.converters.model_to_json import point_models_to_json
from coordextract.point import PointModel


@pytest.fixture
def example_point_models() -> list[PointModel]:
    """Returns a list of example PointModel objects.

    Each PointModel object represents a point with its coordinates and other attributes.

    Returns:
        list: A list of PointModel objects.
    """
    return [
        PointModel(
            gpxpoint="waypoint",
            latitude=0.0,
            longitude=0.0,
            mgrs="31U BT 00000 00000",
        ),
        PointModel(
            gpxpoint="trackpoint",
            latitude=1.1,
            longitude=1.1,
            mgrs="31U BT 11111 11111",
        ),
    ]


def test_point_models_to_json_to_file(
    example_point_models: list[PointModel], tmp_path: Path
) -> None:
    """Test function to verify the correctness of the
    point_models_to_json function by writing the output to a file and
    checking its content.

    Args:
        example_point_models (list[PointModel]): List of example PointModel objects.
        tmp_path (Path): Temporary path for creating the output file.

    Returns:
        None
    """
    file_path = tmp_path / "output.json"
    point_models_to_json(example_point_models, filename=str(file_path))

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "31U BT 00000 00000" in content
    assert "31U BT 11111 11111" in content


def test_point_models_to_json_to_stdout(
    example_point_models: list[PointModel],
) -> None:
    """Test the function point_models_to_json by checking if the
    generated JSON string contains the expected coordinates.

    Args:
        example_point_models (list[PointModel]): List of example PointModel objects.
        capsys (pytest.CaptureFixture[str]): Fixture for capturing stdout.

    Returns:
        None
    """
    json_str = point_models_to_json(example_point_models, filename=None)
    assert json_str is not None and "31U BT 00000 00000" in json_str
    assert json_str is not None and "31U BT 11111 11111" in json_str


def test_point_models_to_json_with_indentation(
    example_point_models: list[PointModel],
) -> None:
    """Test the point_models_to_json function with indentation.

    Args:
        example_point_models (list[PointModel]): List of example PointModel objects.

    Returns:
        None
    """
    json_str = point_models_to_json(
        example_point_models, filename=None, indentation=4
    )
    assert (
        json_str is not None and '    "mgrs": "31U BT 00000 00000"' in json_str
    )


@patch("builtins.open", new_callable=mock_open)
def test_point_models_to_json_file_error(
    mock_file_open: MagicMock, example_point_models: list[PointModel]
) -> None:
    """Test case to verify that an OSError is raised when there is an
    error writing to the file.

    Args:
        mock_open: A mock object for the `open` function.
        example_point_models: A list of example PointModel objects.

    Raises:
        OSError: If there is an error writing to the file.

    Returns:
        None
    """
    mock_file_open.side_effect = OSError("Mocked error")
    with pytest.raises(OSError) as exc_info:
        point_models_to_json(
            example_point_models, filename="nonexistent/path/output.json"
        )
    assert "Error writing to file" in str(exc_info.value)
