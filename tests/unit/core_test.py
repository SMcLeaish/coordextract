"""This module contains unit tests for the factory module in the
coordextract package."""

# pylint: disable=R0903

from pathlib import Path
from typing import Any, Literal, Type, cast
from unittest.mock import MagicMock, AsyncMock, patch, call

import pytest
from magika.types import MagikaResult  # type: ignore

from coordextract.core import CoordExtract, GPXHandler, JSONHandler

###############################################################################
# process_coords tests
###############################################################################
@pytest.mark.asyncio
@patch('coordextract.core.CoordExtract._factory')
@patch('coordextract.point.PointModel')
async def test_process_coords_valid_input(mock_pointmodel_instance: MagicMock,\
                                          mock_factory: MagicMock)-> None:
    """Test the process_coords function with valid input."""
    input_path = Path('/path/to/input')
    output_path = Path('/path/to/output')
    indentation = 4
    concurrency = False
    context = 'some_context'
    input_handler_mock = AsyncMock()
    input_handler_mock.process_input.return_value = [mock_pointmodel_instance]
    output_handler_mock = AsyncMock()
    output_handler_mock.process_output.return_value = None
    mock_factory.side_effect = [input_handler_mock, output_handler_mock]
    result = await CoordExtract.process_coords(input_path, output_path,\
                                               indentation, concurrency,\
                                               context)
    assert result is None
    mock_factory.assert_has_calls([
        call(input_path, concurrency, context),
        call(output_path, concurrency, context),
    ])
    input_handler_mock.process_input.assert_awaited_once()
    output_handler_mock.process_output.assert_awaited_once_with(
        [mock_pointmodel_instance], indentation)


@pytest.mark.asyncio
@patch('coordextract.core.CoordExtract._factory')
@patch('coordextract.point.PointModel')
async def test_process_coords_valid_input_no_output(
                                          mock_pointmodel_instance: MagicMock,\
                                          mock_factory: MagicMock)-> None:
    """Test the process_coords function with valid input."""
    input_path = Path('/path/to/input')
    output_path = None
    indentation = 4
    concurrency = False
    context = 'some_context'
    input_handler_mock = AsyncMock()
    input_handler_mock.process_input.return_value = [mock_pointmodel_instance]
    output_handler_mock = AsyncMock()
    output_str='some_output'
    output_handler_mock.process_output.return_value = output_str
    mock_factory.side_effect = [input_handler_mock, output_handler_mock]
    result = await CoordExtract.process_coords(input_path, output_path,\
                                               indentation, concurrency,\
                                               context)
    assert result == output_str
    mock_factory.assert_has_calls([
        call(input_path, concurrency, context),
        call(output_path, concurrency, context),
    ])
    input_handler_mock.process_input.assert_awaited_once()
    output_handler_mock.process_output.assert_awaited_once_with(
        [mock_pointmodel_instance], indentation)
@pytest.mark.asyncio
@patch('coordextract.core.CoordExtract._factory')
@patch('coordextract.point.PointModel')
async def test_process_coords_valid_input_no_output_str(
                                          mock_pointmodel_instance: MagicMock,\
                                          mock_factory: MagicMock)-> None:
    """Test the process_coords function with valid input."""
    input_path = Path('/path/to/input')
    output_path = None
    indentation = 4
    concurrency = False
    context = 'some_context'
    input_handler_mock = AsyncMock()
    input_handler_mock.process_input.return_value = [mock_pointmodel_instance]
    output_handler_mock = AsyncMock()
    output_str='some_output'
    output_handler_mock.process_output.return_value = None
    mock_factory.side_effect = [input_handler_mock, output_handler_mock]
    result = await CoordExtract.process_coords(input_path, output_path,\
                                               indentation, concurrency,\
                                               context)
    assert result is None
    mock_factory.assert_has_calls([
        call(input_path, concurrency, context),
        call(output_path, concurrency, context),
    ])
    input_handler_mock.process_input.assert_awaited_once()
    output_handler_mock.process_output.assert_awaited_once_with(
        [mock_pointmodel_instance], indentation)

@pytest.mark.asyncio
@patch('coordextract.core.CoordExtract._factory')
async def test_process_coords_error_condition(mock_factory: MagicMock) -> None:
    """Test the process_coords function with an error condition."""
    input_path = Path('/path/to/input')
    input_handler_mock = AsyncMock()
    input_handler_mock.process_input.return_value = None
    mock_factory.return_value = input_handler_mock
    with pytest.raises(ValueError):
        await CoordExtract.process_coords(input_path)
    input_handler_mock.process_input.assert_awaited_once()
###############################################################################
# _get_mimetype tests
###############################################################################
class MockMagikaResult:
    """A mock class representing the result of a Magika operation.

    Attributes:
        output (Any): The output of the Magika operation.
    """

    def __init__(self, output: Any) -> None:
        self.output = output

class MockOutput:
    """A class representing mock output with a specified MIME type.

    Attributes:
        mime_type (str): The MIME type of the mock output.
    """

    def __init__(self, mime_type: Any) -> None:
        self.mime_type = mime_type

@pytest.mark.parametrize(
    "file_path, expected_mime, magika_mime_type",
    [
        (Path("/path/to/file.gpx"), "application/gpx+xml", "text/xml"),
        (Path("/path/to/file.json"), "application/json", None),
    ],
)
@patch("coordextract.core.Magika")
def test_get_mimetype(
    mock_magika_class: MagicMock,
    file_path: Path,
    expected_mime: Literal["application/gpx+xml", "application/json"],
    magika_mime_type: Literal["text/xml", None],
) -> None:
    """Test the get_mimetype function.

    Args:
        mock_magika_class: Mocked Magika class.
        file_path: Path to the file.
        expected_mime: Expected MIME type.
        magika_mime_type: Magika MIME type or None.

    Returns:
        None
    """
    mock_output = MockOutput(mime_type=magika_mime_type)
    mock_magika_result = MockMagikaResult(output=mock_output)
    mock_magika_instance = mock_magika_class.return_value
    mock_magika_instance.identify_path.return_value = mock_magika_result
    # pylint: disable=protected-access
    mimetype, magika_result = CoordExtract._get_mimetype(file_path)
    # pylint: enable=protected-access
    magika_result = cast(MagikaResult, magika_result)
    assert mimetype == expected_mime, "MIME type mismatch"
    if magika_mime_type is not None:
        assert (
            magika_result.output.mime_type == magika_mime_type
        ), "Magika MIME type mismatch"
    else:
        assert magika_result is None or magika_result.output.mime_type is None
    mock_magika_instance.identify_path.assert_called_once_with(file_path)

###############################################################################
# _factory tests
###############################################################################


@pytest.mark.parametrize(
    "file_name, expected_handler_type, mime_type, magika_mime_type",
    [
        ("test.gpx", GPXHandler, "application/gpx+xml", "text/xml"),
        ("test.json", JSONHandler, "application/json", None),
        (None, JSONHandler, None, None),
    ],
)

@patch("coordextract.core.CoordExtract._get_mimetype")
def test_handler_factory(
    mock_get_mimetype: MagicMock,
    file_name: Literal["test.gpx", "test.json"] | None,
    expected_handler_type: Type[CoordExtract],
    mime_type: Literal["application/gpx+xml", "application/json"] | None,
    magika_mime_type: Literal["text/xml"] | None,
    ) -> None:
    """
    Test the handler_factory function.

    Args:
        mock_get_mimetype: Mocked get_mimetype function.
        file_name: Name of the file.
        expected_handler_type: Expected type of the handler.
        mime_type: MIME type of the file.
        magika_mime_type: Magika MIME type.

    Returns:
        None
    """
    mock_output = MockOutput(mime_type=magika_mime_type or "")
    mock_magika_result = MockMagikaResult(output=mock_output)
    mock_get_mimetype.return_value = (mime_type, mock_magika_result)
    file_path = Path(file_name) if file_name is not None else None
    # pylint: disable=protected-access
    handler = CoordExtract._factory(file_path)
    # pylint: enable=protected-access
    assert isinstance(
        handler, expected_handler_type
    ), f"Expected handler type mismatch for {file_name}"
    if file_name is not None:
        mock_get_mimetype.assert_called_once_with(file_path)
    else:
        mock_get_mimetype.assert_not_called()


@patch("coordextract.core.CoordExtract._get_mimetype")
def test_handler_factory_indeterminate_file_type(mock_get_mimetype: MagicMock)\
    -> None:
    """
    Test the handler_factory function when the file type is indeterminate.

    Args:
        mock_get_mimetype: Mocked get_mimetype function.

    Returns:
        None
    """
    mock_get_mimetype.return_value = (None, None)
    with pytest.raises(ValueError) as excinfo:
        #pylint: disable=protected-access
        CoordExtract._factory(Path("indeterminate.file"))
        #pylint: enable=protected-access
    assert "Could not determine the filetype of" in str(excinfo.value)


@patch("coordextract.core.CoordExtract._get_mimetype")
def test_handler_factory_unsupported_file_type(mock_get_mimetype: MagicMock)\
    -> None:
    """
    Test the handler_factory function when the file type is unsupported.

    Args:
        mock_get_mimetype: Mocked get_mimetype function.

    Returns:
        None
    """
    mock_get_mimetype.return_value = ("application/unsupported", MagicMock())
    with pytest.raises(ValueError) as excinfo:
        #pylint: disable=protected-access
        CoordExtract._factory(Path("unsupported.file"))
        #pylint: enable=protected-access
    assert "Unsupported file type for" in str(excinfo.value)

###############################################################################
# GPXHandler tests
###############################################################################

@pytest.mark.asyncio
@patch("coordextract.core.GPXUtils.process_gpx")
async def test_gpx_handler_process_input(mock_process_gpx: MagicMock) -> None:
    """
    Test the process_input function of the GPXHandler class.

    Args:
        mock_process_gpx: Mocked process_gpx function.

    Returns:
        None
    """
    file_path = Path("/path/to/file.gpx")
    concurrency = False
    context = "some_context"
    gpx_handler = GPXHandler(file_path, concurrency, context)
    await gpx_handler.process_input()
    mock_process_gpx.assert_awaited_once_with(file_path)

@pytest.mark.asyncio
@patch("coordextract.point.PointModel")
async def test_gpx_handler_process_output(mock_pointmodel_instance: MagicMock)\
    -> None:
    """
    Test the process_output function of the GPXHandler class.

    Returns:
        None
    """
    with pytest.raises(NotImplementedError) as excinfo:
        file_path = Path("/path/to/file.gpx")
        concurrency = False
        context = "some_context"
        gpx_handler = GPXHandler(file_path, concurrency, context)
        await gpx_handler.process_output([mock_pointmodel_instance], 4)
    assert "Only JSON output is supported." in str(excinfo.value)

###############################################################################
# JSONHandler tests
###############################################################################

@pytest.mark.asyncio
async def test_json_handler_process_input() -> None:
    """
    Test the process_input function of the JSONHandler class.

    Returns:
        None
    """
    with pytest.raises(NotImplementedError) as excinfo:
        file_path = Path("/path/to/file.json")
        concurrency = False
        context = "some_context"
        json_handler = JSONHandler(file_path, concurrency, context)
        await json_handler.process_input()
    assert "Only GPX input is supported." in str(excinfo.value)

@pytest.mark.asyncio
@patch("coordextract.core.JSONHandler._point_models_to_json")
@patch("coordextract.point.PointModel")
async def test_json_handler_process_output(mock_pointmodel_instance:\
                                           MagicMock,\
                                           mock_point_models_to_json:\
                                           MagicMock)-> None:
    """
    Test the process_output function of the JSONHandler class.

    Args:
        mock_point_models_to_json: Mocked _point_models_to_json function.

    Returns:
        None
    """
    file_path = Path("/path/to/file.json")
    concurrency = False
    context = "some_context"
    mpi = mock_pointmodel_instance
    json_handler = JSONHandler(file_path, concurrency, context)
    point_models = [mpi]
    await json_handler.process_output(point_models, 4)
    mock_point_models_to_json.assert_awaited_once_with(point_models,\
                                                       str(file_path),4)
