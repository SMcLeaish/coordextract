"""This module tests the file handler module."""

from unittest.mock import patch, MagicMock
from typing import Generator, cast
from pathlib import Path
import pytest

# watch for Magika type stubs to be released
from magika.types import MagikaResult, MagikaOutputFields  # type: ignore
from coordextract.handler import get_mimetype, inputhandler, outputhandler
from coordextract.models.point import PointModel


@pytest.fixture
def mock_magicka_identify_path_success() -> Generator[MagicMock, None, None]:
    """Mocks the magika classes MagikaResult and MagikaOutputFields."""
    mock_magika_result = MagicMock(spec=MagikaResult)
    mock_output_fields = MagikaOutputFields(
        ct_label="some_label",
        score=0.99,
        group="some_group",
        mime_type="text/xml",
        magic="magic_string",
        description="some_description",
    )
    mock_magika_result.output = mock_output_fields

    with patch(
        "magika.Magika.identify_path", return_value=mock_magika_result
    ) as mock_identify_path:
        yield mock_identify_path


def test_get_mimetype_success(mock_magicka_identify_path_success: MagicMock) -> None:
    """Tests the mimetype function with mocked successful data."""
    with patch(
        "mimetypes.guess_type", return_value=("application/gpx+xml", None)
    ) as mock_mimetypes:
        mimetype, magika_result = get_mimetype(Path("dummy.gpx"))
        assert (
            mimetype == "application/gpx+xml"
        ), "Should be returned on get_mimetype call"
        magika_result = cast(MagikaResult, magika_result)
        assert (
            magika_result.output.mime_type == "text/xml"
        ), "Should also be returned on get_mimetype call"
        mock_mimetypes.assert_called_once_with(str(Path("dummy.gpx")))
        mock_magicka_identify_path_success.assert_called_once_with(Path("dummy.gpx"))


@pytest.mark.asyncio
async def test_inputhandler_unsupported_filetype(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Tests error handling for an unsupported mimetype."""
    with patch(
        "mimetypes.guess_type", return_value=("unsupported/mimetype", None)
    ), patch(
        "magika.Magika.identify_path",
        return_value=MagicMock(output=MagicMock(mime_type="unsupported/mime_type")),
    ):
        with pytest.raises(ValueError) as exc_info:
            await inputhandler(Path("dummy.unsupported"))

        assert "Unsupported filetype" in str(
            exc_info.value
        ), "Should raise an error for \
            an unsupported filetype"


@pytest.mark.asyncio
async def test_inputhandler_unsupported_no_filetype(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Tests error handling for a missing mimetype."""
    with patch("mimetypes.guess_type", return_value=(None, None)), patch(
        "magika.Magika.identify_path",
        return_value=MagicMock(output=MagicMock(mime_type="unsupported/mime_type")),
    ):
        with pytest.raises(ValueError) as exc_info:
            await inputhandler(Path("dummy.unsupported"))

        assert "Could not determine the filetype of" in str(
            exc_info.value
        ), "Should raise an error for \
            a missing mimetype"


async def mock_process_gpx_to_point_models(_file_path: str) -> list[PointModel]:
    """Creates a mock call to gpx_to_point_model to create a
    PointModel."""
    mock_point = PointModel(
        name="Test Point",
        gpxpoint="waypoint",
        latitude=34.12345,
        longitude=-117.12345,
        mgrs="11SPA1234567890",
    )
    return [mock_point]


@pytest.mark.asyncio
async def test_inputhandler_returns_pointmodel_list() -> None:
    """Tests that process_gpx_to_point_models is called correctly on
    valid mime types."""
    mock_magika_result = MagicMock()
    mock_magika_result.output.mime_type = "text/xml"

    with patch(
        "mimetypes.guess_type", return_value=("application/gpx+xml", None)
    ), patch("magika.Magika.identify_path", return_value=mock_magika_result), patch(
        "coordextract.handler.process_gpx_to_point_models",
        side_effect=mock_process_gpx_to_point_models,
    ):
        result = await inputhandler(Path("dummy.gpx"))
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], PointModel), "Should create a single PointModel"


@pytest.fixture
def point_models() -> list[MagicMock]:
    """Creates a list of 3 PointModel objects."""
    return [MagicMock(spec=PointModel) for _ in range(3)]


@patch("coordextract.handler.point_models_to_json")
@patch("coordextract.handler.get_mimetype")
def test_outputhandler_json_file(
    mock_get_mimetype: MagicMock, mock_to_json: MagicMock, point_models: list[MagicMock]
) -> None:
    """Tests ouputhandler with json filetype."""
    mock_get_mimetype.return_value = ("application/json", None)
    test_filename = Path("test.json")
    cast_point_models = cast(list[PointModel], point_models)
    outputhandler(cast_point_models, test_filename, 4)
    mock_to_json.assert_called_once_with(cast_point_models, str(test_filename), 4)


@patch("coordextract.handler.get_mimetype")
def test_outputhandler_unsupported_filetype(
    mock_get_mimetype: MagicMock, point_models: list[MagicMock]
) -> None:
    """Tests outputhandler with unsupported filetype."""
    mock_get_mimetype.return_value = ("text/plain", None)
    cast_point_models = cast(list[PointModel], point_models)
    with pytest.raises(ValueError) as exc_info:
        outputhandler(
            cast_point_models,
            Path("test.txt"),
            4,
        )
    assert "Unsupported output file type: text/plain" in str(
        exc_info.value
    ), "Should raise a value error."


@patch("coordextract.handler.point_models_to_json")
def test_outputhandler_no_file(
    mock_to_json: MagicMock, point_models: list[MagicMock]
) -> None:
    """Tests outputhandler with no file given."""
    cast_point_models = cast(list[PointModel], point_models)
    outputhandler(cast_point_models, None, None)
    mock_to_json.assert_called_once_with(point_models, None, None)
