"""
"""

from pathlib import Path
from unittest.mock import mock_open, patch
import pytest
from coordextract.exporters.model_to_json import point_models_to_json
from coordextract import PointModel


@pytest.fixture
def example_point_models():
    return [
        PointModel(
            name="Test Point 1", latitude=0.0, longitude=0.0, mgrs="31U BT 00000 00000"
        ),
        PointModel(
            name="Test Point 2", latitude=1.1, longitude=1.1, mgrs="31U BT 11111 11111"
        ),
    ]


def test_point_models_to_json_to_file(
    example_point_models: list[PointModel], tmp_path: Path
):
    file_path = tmp_path / "output.json"
    point_models_to_json(example_point_models, filename=str(file_path))

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Test Point 1" in content
    assert "Test Point 2" in content


def test_point_models_to_json_to_stdout(
    example_point_models: list[PointModel], capsys: pytest.CaptureFixture[str]
):
    point_models_to_json(example_point_models, filename=None)
    captured = capsys.readouterr()
    assert "Test Point 1" in captured.out
    assert "Test Point 2" in captured.out


def test_point_models_to_json_with_indentation(
    example_point_models: list[PointModel], capsys: pytest.CaptureFixture[str]
):
    point_models_to_json(example_point_models, filename=None, indentation=4)
    captured = capsys.readouterr()
    assert '    "name": "Test Point 1"' in captured.out


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
