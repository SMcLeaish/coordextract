"""This module contains unit tests for the `coordextract.cli` module.

It tests various functionalities of the command-line interface (CLI)
provided by the `coordextract` package.
"""

from pathlib import Path
import tempfile
from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest
from typer.testing import CliRunner

from coordextract.cli import app, process, process_batch, process_directory

runner = CliRunner()


@pytest.fixture
def temp_dir_with_file() -> Generator[tuple[str, Path], None, None]:
    """Create a temporary directory with a file."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpfile = Path(tmpdirname) / "inputfile.gpx"
        tmpfile.write_text("dummy test")
        yield tmpdirname, tmpfile


@pytest.fixture
def temp_files(
    temp_dir_with_file: tuple[Path, Path]
) -> Generator[list[Path], None, None]:
    """Create a temporary directory with multiple files."""
    tmpdirname_str, _ = temp_dir_with_file
    tmpdirname = Path(tmpdirname_str)
    files = [tmpdirname / f"file{i}.txt" for i in range(3)]
    for file in files:
        file.write_text("dummy content")
    yield files


@pytest.fixture
def gpx_directory() -> Generator[tuple[Path, Path], None, None]:
    """Create a temporary directory with .gpx files."""
    with tempfile.TemporaryDirectory() as tmpinputdir:
        inputdir = Path(tmpinputdir)
        for i in range(3):
            (inputdir / f"file{i}.gpx").write_text(f"GPX content {i}")

        with tempfile.TemporaryDirectory() as tmpoutputdir:
            outputdir = Path(tmpoutputdir)
            yield inputdir, outputdir


def test_main_no_input() -> None:
    """Test the main function with no input."""
    result = runner.invoke(app, [])
    assert result.exit_code == 2
    assert "Try" in result.stdout


@patch("coordextract.cli.process", new_callable=AsyncMock)
def test_cli_with_temporary_file(
    mock_process: AsyncMock, temp_dir_with_file: tuple[str, Path]
) -> None:
    """Test the main function with an input file."""
    tmpdirname, tmpfile = temp_dir_with_file
    result = runner.invoke(
        app,
        [
            str(tmpfile),
            "--output",
            f"{tmpdirname}/outputfile.json",
            "--indent",
            "2",
            "--concurrency",
        ],
    )
    assert result.exit_code == 0
    expected_input_path = tmpfile.resolve()
    expected_output_path = Path(f"{tmpdirname}/outputfile.json")

    mock_process.assert_awaited_once_with(
        expected_input_path, expected_output_path, 2, True
    )


@patch("coordextract.cli.process_directory", new_callable=AsyncMock)
def test_cli_with_temporary_directory(
    mock_process_directory: AsyncMock, gpx_directory: tuple[Path, Path]
) -> None:
    """Test the main function with a directory."""
    inputdir, outputdir = gpx_directory
    result = runner.invoke(
        app,
        [
            str(inputdir),
            "--output",
            str(outputdir),
            "--indent",
            "2",
            "--concurrency",
        ],
    )
    assert result.exit_code == 0
    test_inputdir = inputdir.resolve()
    mock_process_directory.assert_awaited_once_with(
        test_inputdir, outputdir, 2, True
    )


@patch("coordextract.cli.process_batch", new_callable=AsyncMock)
def test_cli_with_multiple_files(
    mock_process_batch: AsyncMock, gpx_directory: tuple[Path, Path]
) -> None:
    """Test the main function with a directory and no concurrency."""
    inputdir, _ = gpx_directory
    files = [inputdir / f"file{i}.gpx" for i in range(3)]
    absfiles = [file.resolve() for file in files]

    result = runner.invoke(
        app, [str(file) for file in files] + ["--indent", "2"]
    )
    for i in range(3):
        assert (inputdir / f"file{i}.gpx").exists()

    assert result.exit_code == 0
    mock_process_batch.assert_awaited_once_with(absfiles, Path("."), 2, False)


@patch("coordextract.cli.process", new_callable=AsyncMock)
def test_main_with_bad_value(
    mock_process: AsyncMock, temp_dir_with_file: tuple[str, Path]
) -> None:
    """Test the main function catches exceptions."""
    mock_process.side_effect = ValueError("Test exception")
    tmpdirname, tmpfile = temp_dir_with_file
    result = runner.invoke(
        app,
        [
            str(tmpfile),
            "--output",
            f"{tmpdirname}/outputfile.json",
            "--indent",
            "2",
            "--concurrency",
        ],
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
    mock_pc.assert_awaited_once_with(Path("dummy.gpx"), None, 2, False, "cli")


@pytest.mark.asyncio
@patch("coordextract.cli.pc", new_callable=AsyncMock)
async def test_process_raises_exception(mock_pc: AsyncMock) -> None:
    """Test the process function that raises an exception."""
    mock_pc.side_effect = ValueError("Test exception")
    inputfile = Path("dummy.gpx")
    outputfile = Path("output.json")
    indentation = 2

    with pytest.raises(ValueError) as excinfo:
        await process(inputfile, outputfile, indentation)

    assert "Test exception" in str(excinfo.value)


@pytest.mark.asyncio
@patch("coordextract.cli.pc", new_callable=AsyncMock)
async def test_process_batch(
    mock_pc: AsyncMock, temp_files: list[Path]
) -> None:
    """Test the process_batch function."""
    outputdir = Path(temp_files[0].parent, "output")
    await process_batch(temp_files, outputdir, 2, concurrency=True)
    assert outputdir.exists()
    for file in temp_files:
        expected_output_file = outputdir / f"{file.stem}.json"
        mock_pc.assert_any_await(file, expected_output_file, 2, True)
    assert mock_pc.await_count == len(temp_files)


@pytest.mark.asyncio
@patch("coordextract.cli.process_batch", new_callable=AsyncMock)
async def test_process_directory(
    mock_process_batch: AsyncMock, gpx_directory: tuple[Path, Path]
) -> None:
    """Test the process_directory function."""
    inputdir, outputdir = gpx_directory
    await process_directory(
        inputdir, outputdir, indentation=2, concurrency=False
    )
    assert mock_process_batch.await_count == 1
    mock_process_batch.assert_awaited_with(
        [inputdir / f"file{i}.gpx" for i in range(3)], outputdir, 2, False
    )
