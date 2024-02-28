"""This module contains unit tests for the `coordextract.cli` module.

It tests various functionalities of the command-line interface (CLI)
provided by the `coordextract` package.
"""

from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
import pytest
from typer.testing import CliRunner
from coordextract.cli import app, process

runner = CliRunner()


def test_main_no_input() -> None:
    """Test the main function with no input."""
    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout


@patch("coordextract.cli.process")
def test_main_with_inputfile(mock_process: MagicMock) -> None:
    """Test the main function with an input file."""
    mock_process.return_value = None
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

    mock_process.assert_called_once_with(
        Path("path/to/inputfile.gpx"), Path("path/to/outputfile.json"), 2
    )
    assert result.exit_code == 0


@patch("coordextract.cli.process")
def test_main_with_bad_value(mock_process: MagicMock) -> None:
    """Test the main function with an input file."""
    mock_process.side_effect = ValueError("Test exception")
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

    mock_process.assert_called_once_with(
        Path("path/to/inputfile.gpx"), Path("path/to/outputfile.json"), 2
    )
    assert result.exit_code == 1


@pytest.mark.asyncio
@patch("coordextract.cli.pc")
async def test_process_file_with_valid_input_and_output(
    mock_pc: AsyncMock,
) -> None:
    """Test the process function with valid input and output files."""
    mock_pc.return_value = None
    await mock_pc(Path("dummy.gpx"), Path("dummy.json"), 2)
    mock_pc.assert_called_once_with(Path("dummy.gpx"), Path("dummy.json"), 2)


@pytest.mark.asyncio
@patch("coordextract.cli.process")
async def test_pc_functionality(mock_process: AsyncMock) -> None:
    """Test the pc functionality."""
    await mock_process(Path("dummy.gpx"), None, 2)
    mock_process.assert_awaited_once_with(Path("dummy.gpx"), None, 2)


@pytest.mark.asyncio
@patch("coordextract.cli.pc", new_callable=AsyncMock)
async def test_process_calls_pc_and_handles_output_correctly(
    mock_pc: AsyncMock, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test the process function that calls pc and handles the output
    correctly."""
    expected_json_str = '{"latitude": 40.7128, "longitude": -74.006}'
    mock_pc.return_value = expected_json_str
    await process(Path("dummy.gpx"), None, 2)
    captured = capsys.readouterr()
    assert expected_json_str in captured.out
    mock_pc.assert_awaited_once_with(Path("dummy.gpx"), None, 2)


@pytest.mark.asyncio
@patch(
    "coordextract.cli.pc", new_callable=AsyncMock
)  # Adjust the path according to your project structure
async def test_process_raises_exception(mock_pc: AsyncMock) -> None:
    """Test the process function that raises an exception."""
    mock_pc.side_effect = ValueError("Test exception")
    inputfile = Path("dummy.gpx")
    outputfile = Path("output.json")
    indentation = 2

    with pytest.raises(ValueError) as excinfo:
        await process(inputfile, outputfile, indentation)

    assert "Test exception" in str(excinfo.value)
