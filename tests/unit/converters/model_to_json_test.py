"""
"""

from pathlib import Path
from unittest.mock import mock_open, patch
import pytest
from coordextract.converters.model_to_json import point_models_to_json
from coordextract.models.point import PointModel


@pytest.fixture
def example_point_models():
    return [
        PointModel(
            gpxpoint="waypoint", latitude=0.0, longitude=0.0, mgrs="31U BT 00000 00000"
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
):
    file_path = tmp_path / "output.json"
    point_models_to_json(example_point_models, filename=str(file_path))

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "31U BT 00000 00000" in content
    assert "31U BT 11111 11111" in content


def test_point_models_to_json_to_stdout(
    example_point_models: list[PointModel], capsys: pytest.CaptureFixture[str]
):
    json_str = point_models_to_json(example_point_models, filename=None)
    assert "31U BT 00000 00000" in json_str
    assert "31U BT 11111 11111" in json_str


def test_point_models_to_json_with_indentation(example_point_models: list[PointModel]):
    json_str = point_models_to_json(example_point_models, filename=None, indentation=4)
    assert '    "mgrs": "31U BT 00000 00000"' in json_str


@patch("builtins.open", new_callable=mock_open)
def test_point_models_to_json_file_error(
    mock_open, example_point_models: list[PointModel]
):
    mock_open.side_effect = OSError("Mocked error")
    with pytest.raises(OSError) as exc_info:
        point_models_to_json(
            example_point_models, filename="nonexistent/path/output.json"
        )
    assert "Error writing to file" in str(exc_info.value)
