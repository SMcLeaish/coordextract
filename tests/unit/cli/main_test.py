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
async def test_main_with_coords()->None:
    """Tests the main function's ability to process direct coordinate
    inputs provided via command line arguments, ensuring correct
    conversion and output."""
    result = runner.invoke(app, ["--coords", "40.7128,-74.0060"])
    assert result.exit_code == 0
    assert "18TWL8395907350" in result.stdout


@pytest.mark.asyncio
async def test_main_with_invalid_coords()->None:
    """Tests the main function's response to invalid coordinate inputs,
    verifying that it correctly identifies and reports format errors."""
    result = runner.invoke(app, ["--coords", "not,a,coordinate"])
    assert result.exit_code == 1
    assert "Invalid latitude and longitude format" in result.stdout


@pytest.mark.asyncio
async def test_main_no_input()->None:
    """Tests the main function's behavior when no inputs are provided,
    ensuring the display of usage instructions."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


@patch("coordextract.cli.main.process_file")
def test_main_with_inputfile(mock_process_file: MagicMock)->None:
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
@patch("coordextract.cli.main.inputhandler", new_callable=AsyncMock)
async def test_process_file_valid_input(mock_inputhandler: AsyncMock)-> None:
    """Tests processing of a valid input file, ensuring the input
    handler function is called with the correct file path."""
    await process_file(Path("dummy.gpx"), None, 2)
    mock_inputhandler.assert_called_once_with(Path("dummy.gpx"))


@pytest.mark.asyncio
@patch("coordextract.cli.main.inputhandler", new_callable=AsyncMock)
async def test_process_file_inputhandler_returns_none(mock_inputhandler: AsyncMock)->None:
    """Tests the behavior of the process_file function when the input
    handler returns None, verifying error handling and messaging."""
    mock_inputhandler.return_value = None
    with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
        with pytest.raises(SystemExit) as e:
            await process_file(Path("dummy.gpx"), Path("dummy.json"), 2)
        mock_inputhandler.assert_called_once_with(Path("dummy.gpx"))
        assert (
            "Error: File handler returned None. Check the input file path"
            in mock_stderr.getvalue()
        )
    assert e.value.code == 1


@pytest.mark.asyncio
@patch("coordextract.cli.main.inputhandler", new_callable=AsyncMock)
async def test_process_file_with_value_error_direct_handling(mock_inputhandler: AsyncMock)->None:
    """Tests the process_file function's error handling capabilities
    when a ValueError is raised during processing, ensuring appropriate
    error messages are logged."""
    mock_inputhandler.side_effect = ValueError("An error occurred")

    with patch("sys.stderr", new=io.StringIO()) as mock_stderr:
        with pytest.raises(SystemExit) as sys_exit:
            await process_file(Path("dummy.gpx"), None, 2)

        assert "An error occurred" in mock_stderr.getvalue()
        assert sys_exit.value.code == 1


@pytest.mark.asyncio
@patch("coordextract.cli.main.outputhandler", new_callable=MagicMock)
async def test_process_file_calls_outputhandler_correctly(
    mock_outputhandler: MagicMock,
)->None:
    """Tests whether the process_file function correctly calls the
    output handler with the expected arguments, ensuring proper data
    flow through the application."""
    mock_result = MagicMock()
    with patch(
        "coordextract.cli.main.inputhandler",
        new_callable=AsyncMock,
        return_value=mock_result,
    ) as mock_inputhandler:
        await process_file(Path("dummy.gpx"), Path("dummy.json"), 2)
        mock_inputhandler.assert_called_once_with(Path("dummy.gpx"))
    mock_outputhandler.assert_called_once_with(mock_result, Path("dummy.json"), 2)
