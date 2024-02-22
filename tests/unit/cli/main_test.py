"""This module provides CLI tools for extracting coordinates from
various formats and converting them into a specified output format.

It supports direct latitude and longitude inputs, file inputs, and
customization of output formats and indentation levels. The main
functionality revolves around processing input data to generate
geospatially relevant output, making it useful for GIS applications and
data processing tasks.
"""

from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
import io
import pytest
from typer.testing import CliRunner
from coordextract.cli.main import app, process_file

runner = CliRunner()


@pytest.mark.asyncio
async def test_main_with_coords() -> None:
    """Tests the main function's ability to process direct coordinate
    inputs provided via command line arguments, ensuring correct
    conversion and output."""
    result = runner.invoke(app, ["--coords", "40.7128,-74.0060"])
    assert result.exit_code == 0
    assert "18TWL8395907350" in result.stdout


@pytest.mark.asyncio
async def test_main_with_invalid_coords() -> None:
    """Tests the main function's response to invalid coordinate inputs,
    verifying that it correctly identifies and reports format errors."""
    result = runner.invoke(app, ["--coords", "not,a,coordinate"])
    assert result.exit_code == 1
    assert "Invalid latitude and longitude format" in result.stdout


@pytest.mark.asyncio
async def test_main_no_input() -> None:
    """Tests the main function's behavior when no inputs are provided,
    ensuring the display of usage instructions."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


@patch("coordextract.cli.main.process_file")
def test_main_with_inputfile(mock_process_file: MagicMock) -> None:
    """Tests the main function's ability to handle file input arguments,
    checking if the file processing function is called with correct
    parameters."""
    mock_process_file.return_value = None
    result = runner.invoke(
        app,
        [
            "--file",
            "path/to/inputfile.gpx",
            "--out",
            "path/to/outputfile.json",
            "--indent",
            "2",
        ],
    )

    mock_process_file.assert_called_once_with(
        Path("path/to/inputfile.gpx"), Path("path/to/outputfile.json"), 2
    )
    assert result.exit_code == 0


@pytest.mark.asyncio
@patch("coordextract.cli.main.handler_factory")
async def test_process_file_valid_input(mock_factory: MagicMock) -> None:
    """Tests processing of a valid input and outputfile using a mock
    handler factory."""
    mock_input_handler_instance = AsyncMock()
    mock_input_handler_instance.process_input = AsyncMock(return_value="some_result")
    mock_output_handler_instance = AsyncMock()
    mock_output_handler_instance.process_output = AsyncMock()
    mock_factory.side_effect = [
        mock_input_handler_instance,
        mock_output_handler_instance,
    ]
    with pytest.raises(SystemExit) as e:
        await process_file(Path("dummy.gpx"), Path("dummy.json"), 2)
    assert mock_factory.call_count == 2
    mock_input_handler_instance.process_input.assert_called_once()
    mock_output_handler_instance.process_output.assert_called_once_with(
        "some_result", 2
    )
    assert e.type == SystemExit
    assert e.value.code == 0


@pytest.mark.asyncio
@patch("coordextract.cli.main.handler_factory")
async def test_process_file_inputhandler_returns_none(mock_factory: MagicMock) -> None:
    """Tests the behavior of the process_file function when the input
    handler returns None."""
    mock_input_handler_instance = AsyncMock()
    mock_input_handler_instance.process_input = AsyncMock(return_value=None)
    mock_factory.side_effect = [mock_input_handler_instance]
    with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
        with pytest.raises(SystemExit) as e:
            await process_file(Path("dummy.gpx"), Path("dummy.json"), 2)
        mock_factory.assert_called_once()
        mock_input_handler_instance.process_input.assert_called_once()
        assert (
            "Error: File handler returned None. Check the input file path"
            in mock_stderr.getvalue()
        )
    assert e.value.code == 1


@pytest.mark.asyncio
@patch("coordextract.cli.main.handler_factory")
async def test_process_file_with_value_error_direct_handling(
    mock_factory: MagicMock,
) -> None:
    """Tests the process_file function's error handling capabilities
    when a ValueError is raised during processing."""
    mock_input_handler_instance = AsyncMock()
    mock_input_handler_instance.process_input = AsyncMock()
    mock_factory.side_effect = [mock_input_handler_instance]
    mock_input_handler_instance.process_input.side_effect = ValueError(
        "An error occurred"
    )

    with patch("sys.stderr", new=io.StringIO()) as mock_stderr:
        with pytest.raises(SystemExit) as sys_exit:
            await process_file(Path("dummy.gpx"), None, 2)
        mock_factory.assert_called_once()
        mock_input_handler_instance.process_input.assert_called_once()
        assert "An error occurred" in mock_stderr.getvalue()
        assert sys_exit.value.code == 1


@pytest.mark.asyncio
@patch("coordextract.cli.main.handler_factory")
async def test_process_file_calls_outputhandler_without_outputfile(
    mock_factory: MagicMock,
) -> None:
    """Tests whether the process_file function correctly calls the
    output handler with the expected arguments."""
    mock_result = MagicMock()
    mock_input_handler_instance = AsyncMock()
    mock_input_handler_instance.process_input = AsyncMock(return_value=mock_result)
    mock_output_handler_instance = AsyncMock()
    mock_output_handler_instance.process_output = AsyncMock()
    mock_factory.side_effect = [
        mock_input_handler_instance,
        mock_output_handler_instance,
    ]
    with pytest.raises(SystemExit) as e:
        await process_file(Path("dummy.gpx"), None, 2)
    assert mock_factory.call_count == 2
    mock_input_handler_instance.process_input.assert_called_once()
    mock_output_handler_instance.process_output.assert_called_once_with(mock_result, 2)
    assert e.type == SystemExit
    assert e.value.code == 0
