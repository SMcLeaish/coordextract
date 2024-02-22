"""
This module contains unit tests for the factory module in the coordextract package.
"""

# pylint: disable=R0903

from pathlib import Path
from typing import Literal, Type, cast, Any
from unittest.mock import patch, MagicMock
import pytest
from coordextract.factory import (
    MagikaResult,
    IOHandler,
    GPXHandler,
    JSONHandler,
    handler_factory,
    get_mimetype,
)


@pytest.mark.parametrize(
    "file_path, expected_mime, magika_mime_type",
    [
        (Path("/path/to/file.gpx"), "application/gpx+xml", "text/xml"),
        (Path("/path/to/file.json"), "application/json", None),
    ],
)
@patch("coordextract.factory.Magika")
def test_get_mimetype(
    mock_magika_class: MagicMock,
    file_path: Path,
    expected_mime: Literal["application/gpx+xml", "application/json"],
    magika_mime_type: Literal["text/xml"] | None,
) -> None:
    """
    Test the get_mimetype function.

    Args:
        mock_magika_class: Mocked Magika class.
        file_path: Path to the file.
        expected_mime: Expected MIME type.
        magika_mime_type: Magika MIME type.

    Returns:
        None
    """
    mock_output = MockOutput(mime_type=magika_mime_type)
    mock_magika_result = MockMagikaResult(output=mock_output)
    mock_magika_instance = mock_magika_class.return_value
    mock_magika_instance.identify_path.return_value = mock_magika_result
    mimetype, magika_result = get_mimetype(file_path)
    magika_result = cast(MagikaResult, magika_result)
    assert mimetype == expected_mime, "MIME type mismatch"
    if magika_mime_type is not None:
        assert (
            magika_result.output.mime_type == magika_mime_type
        ), "Magika MIME type mismatch"
    else:
        assert magika_result is None or magika_result.output.mime_type is None
    mock_magika_instance.identify_path.assert_called_once_with(file_path)


@pytest.mark.parametrize(
    "file_name, expected_handler_type, mime_type, magika_mime_type",
    [
        ("test.gpx", GPXHandler, "application/gpx+xml", "text/xml"),
        ("test.json", JSONHandler, "application/json", None),
        (None, JSONHandler, None, None),
    ],
)
@patch("coordextract.factory.get_mimetype")
def test_handler_factory(
    mock_get_mimetype: MagicMock,
    file_name: Literal["test.gpx", "test.json"] | None,
    expected_handler_type: Type[IOHandler],
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
    handler = handler_factory(file_path)
    assert isinstance(
        handler, expected_handler_type
    ), f"Expected handler type mismatch for {file_name}"
    if file_name is not None:
        mock_get_mimetype.assert_called_once_with(file_path)
    else:
        mock_get_mimetype.assert_not_called()


@patch("coordextract.factory.get_mimetype")
def test_handler_factory_indeterminate_file_type(mock_get_mimetype: MagicMock) -> None:
    """
    Test the handler_factory function when the file type is indeterminate.

    Args:
        mock_get_mimetype: Mocked get_mimetype function.

    Returns:
        None
    """
    mock_get_mimetype.return_value = (None, None)
    with pytest.raises(ValueError) as excinfo:
        handler_factory(Path("indeterminate.file"))
    assert "Could not determine the filetype of" in str(excinfo.value)


@patch("coordextract.factory.get_mimetype")
def test_handler_factory_unsupported_file_type(mock_get_mimetype: MagicMock) -> None:
    """
    Test the handler_factory function when the file type is unsupported.

    Args:
        mock_get_mimetype: Mocked get_mimetype function.

    Returns:
        None
    """
    mock_get_mimetype.return_value = ("application/unsupported", MagicMock())
    with pytest.raises(ValueError) as excinfo:
        handler_factory(Path("unsupported.file"))

    assert "Unsupported file type for" in str(excinfo.value)


class MockMagikaResult:
    """
    A mock class representing the result of a Magika operation.

    Attributes:
        output (Any): The output of the Magika operation.
    """

    def __init__(self, output: Any) -> None:
        self.output = output


class MockOutput:
    """
    A class representing mock output with a specified MIME type.

    Attributes:
        mime_type (str): The MIME type of the mock output.
    """

    def __init__(self, mime_type: Any) -> None:
        self.mime_type = mime_type
