"""
This module tests the file handler module. 
"""

from unittest.mock import patch, MagicMock
from typing import Generator, cast
from pathlib import Path
import pytest

# watch for Magika type stubs to be released
from magika.types import MagikaResult, MagikaOutputFields  # type: ignore
from coordextract.handler import get_mimetype


@pytest.fixture
def mock_magicka_identify_path_success() -> Generator[MagicMock, None, None]:
    """
    Mocks the magika classes MagikaResult and MagikaOutputFields
    """
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


def test_get_mimetype(mock_magicka_identify_path_success: MagicMock) -> None:
    """
    Tests the mimetype function with mocked successful data.
    """
    with patch(
        "mimetypes.guess_type", return_value=("application/gpx+xml", None)
    ) as mock_mimetypes:
        mimetype, magika_result = get_mimetype(Path("dummy.gpx"))
        assert mimetype == "application/gpx+xml"
        magika_result = cast(MagikaResult, magika_result)
        assert magika_result.output.mime_type == "text/xml"
        mock_mimetypes.assert_called_once_with(str(Path("dummy.gpx")))
        mock_magicka_identify_path_success.assert_called_once_with(Path("dummy.gpx"))
