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

import sys
from typing import Optional
from pathlib import Path
import asyncio
from typing_extensions import Annotated
import typer
from pydantic import ValidationError
from coordextract import process_coords as pc
from coordextract.point import PointModel
app = typer.Typer()

@app.command()
def main(
    ctx: typer.Context,
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
    """Accepts a GPX file as input and outputs a JSON object with all
    points and converted MGRS. When an output filename is given it will
    write the points to that file.

    Args:
        inputfile (str): Path to the GPX file to process.

        coords (Optional[str]): Comma-separated latitude and longitude for direct MGRS conversion.

        outputfile (Optional[str]): Path to the output JSON file for file processing mode.

        indentation (Optional[int]): Indentation level for the JSON output. Defaults to 2 spaces.
    """
    try:
        if coords:
            try:
                if coords is not None and len(coords.split(",")) == 2:
                    latitude, longitude = map(float, coords.split(","))
                    if PointModel.validate_latitude(latitude):
                        print(PointModel.lat_lon_to_mgrs(latitude, longitude))
                        sys.exit(0)
                if coords is not None and len(coords.split(",")) > 2:
                    raise ValueError("Invalid number of coordinates")
                if len(coords) == 1 and PointModel.validate_mgrs(coords[0]):
                    print(PointModel.mgrs_to_lat_lon(coords[0]))
                    sys.exit(0)
            except ValueError as e:
                raise e
        elif inputfile:
            json_str = asyncio.run(pc(inputfile, outputfile, indentation))
            if json_str is not None:
                print(json_str)
        else:
            print(ctx.get_help())
            raise typer.Exit(code=0)
    except (ValueError, OSError, RuntimeError, NotImplementedError, ValidationError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    app()  # pragma: no cover
