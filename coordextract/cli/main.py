"""Provides a command-line interface (CLI) for processing geographic
data files and converting coordinates.

This CLI supports processing GPX files to extract geographic points and converting latitude and
longitude coordinates to the Military Grid Reference System (MGRS). It allows users to specify 
an input GPX file, an output JSON file with optional indentation, and direct latitude and longitude 
inputs for quick MGRS conversions.

Features:
- Process GPX files to extract geographic points.
- Convert latitude and longitude to MGRS coordinates.
- Export extracted points to a JSON file with optional indentation.

Usage:
- For GPX file processing: `coordextract -f path/to/file.gpx -o output.json -i 2`
- For direct MGRS conversion: `coordextract -c "latitude,longitude"`
"""

from typing import Optional
from pathlib import Path
import asyncio
from typing_extensions import Annotated
import typer
from coordextract.converters import latlon_to_mgrs
from coordextract import inputhandler, outputhandler

app = typer.Typer()


async def process_file(
    inputfile: Path, outputfile: Optional[Path], indentation: Optional[int]
) -> None:
    """Asynchronously processes a geographic data file, outputs the
    results to a specified file or stdout.

    This function serves as the core processing workflow, invoking input handling to parse and
    convert geographic data from the specified input file and then using output handling to
    serialize and write the data to a JSON file or stdout with optional indentation. It provides
    user feedback on the process success or reasons for failure.

    Args:
        inputfile (str): The path to the input file containing geographic data to be processed.
        outputfile (Optional[str]): The path to the output JSON file where the processed data
        should be saved.
        If None, the output will be printed to stdout.

        indentation (Optional[int]): The number of spaces used for JSON output indentation.
        Defaults to 2

    Raises:
        typer.Exit: Exits the CLI application with a non-zero exit code if processing fails due
        to an unhandled file type or other ValueError, or if the input file handler returns
        None, indicating a failure to process the input file.
    """
    try:
        filehandler_result = await inputhandler(inputfile)
        if filehandler_result is not None:
            outputhandler(filehandler_result, outputfile, indentation)
            typer.echo("Processing completed successfully.")
        else:
            typer.echo(
                "Error: File handler returned None. Check the input file path\
                or filehandler implementation.",
                err=True,
            )
            raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1)


@app.command()
def main(
    inputfile: Annotated[
        Optional[Path],
        typer.Option(
            "--file", "-f", help="The file path to process. Accepted formats: gpx"
        ),
    ] = None,
    coords: Optional[str] = typer.Option(
        None,
        "--coords",
        "-c",
        help="A comma-separated latitude and longitude string in quotes for MGRS conversion.",
    ),
    outputfile: Optional[Path] = typer.Option(
        None, "--out", "-o", help="Accepted formats: json "
    ),
    indentation: Optional[int] = typer.Option(
        None,
        "--indent",
        "-i",
        help="Optionally add indentation level to json. Defaults to 2.",
    ),
) -> None:
    """Processes an input file or coordinates for geographic data
    conversion and output handling.

    Depending on the input, this function either processes a GPX file to extract geographic points
    and optionally exports them to a JSON file, or converts a pair of latitude and longitude
    coordinates directly to MGRS.

    Args:
        inputfile (str): Path to the GPX file to process. If provided, triggers file processing.
        coords (Optional[str]): Comma-separated latitude and longitude for direct MGRS conversion.
        outputfile (Optional[str]): Path to the output JSON file for file processing mode.
        indentation (Optional[int]): Indentation level for the JSON output. Defaults to 2 spaces.

    """
    if coords:
        try:
            latitude, longitude = map(float, coords.split(","))
            print(latlon_to_mgrs(latitude, longitude))
        except ValueError as exc:
            print(
                "Invalid latitude and longitude format. \
                Please provide them as quoted comma-separated values."
            )
            raise typer.Exit(code=1) from exc
    elif inputfile:
        asyncio.run(process_file(inputfile, outputfile, indentation))
    else:
        print("No input provided.")
        raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
