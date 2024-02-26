"""This module contains a command-line interface (CLI) for processing
GPX files and converting coordinates to JSON format.

The CLI provides the following functionality:
- Accepts one or multiple GPX files or a directory as input
- Converts the coordinates to JSON format
- Supports writing the JSON output to a file or printing it to the console
- Supports specifying the indentation level for the JSON output

Usage:
    python cli.py [OPTIONS]

Options:
    --file, -f TEXT     The GPX file(s) or directory to process.
    --out, -o TEXT      Output file or directory.
    --indent, -i TEXT   Indentation level for the JSON output. Defaults to 2.
"""

import sys
from typing import Optional
from pathlib import Path
import asyncio
import time
import typer
from pydantic import ValidationError
from coordextract import process_coords as pc


app = typer.Typer()


async def process(
    inputfile: Path,
    outputfile: Optional[Path],
    indentation: Optional[int],
    concurrency: Optional[bool],
) -> Optional[str]:
    """Asynchronously processes the input file and writes the JSON
    output to a file or prints it to the console.

    Args:
        inputfile (Path): The input file to process.
        outputfile (Optional[Path]): The output file to write the JSON to.
        indentation (Optional[int]): The indentation level for the JSON output.

    Returns:
        str: The JSON string.
    """

    json_str = await pc(inputfile, outputfile, indentation, concurrency)
    if json_str is not None:
        print(json_str)
    return None


async def process_batch(
    files: list[Path],
    outputdir: Path,
    indentation: Optional[int],
    concurrency: Optional[bool],
) -> None:
    """Processes a batch of files concurrently."""
    outputdir.mkdir(parents=True, exist_ok=True)
    tasks = [
        asyncio.create_task(
            pc(file, outputdir / f"{file.stem}.json", indentation, concurrency)
        )
        for file in files
    ]
    await asyncio.gather(*tasks)


async def process_directory(
    inputdir: Path,
    outputdir: Path,
    indentation: Optional[int],
    concurrency: Optional[bool],
) -> None:
    """Processes all GPX files in a directory."""
    files = [file for file in inputdir.iterdir() if file.suffix == ".gpx"]
    await process_batch(files, outputdir, indentation, concurrency)


@app.command()
def main(
    inputs: list[Path] = typer.Argument(
        ...,
        exists=True,
        dir_okay=True,
        file_okay=True,
        readable=True,
        resolve_path=True,
        help="The GPX file(s) or directory to process.",
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file or directory."
    ),
    indentation: Optional[int] = typer.Option(
        None, "--indent", "-i", help="Indentation level for the JSON output."
    ),
    concurrency: Optional[bool] = typer.Option(
        False,
        "--concurrency",
        "-c",
        help="Use cpu concurrency for batch processessing large datasets.",
    ),
) -> None:
    """Accepts a GPX file or directory as input and converts the
    coordinates to JSON format. The output JSON object contains all
    points and their corresponding MGRS coordinates.

    Usage:
        python cli.py [OPTIONS]

    Options:
        --file, -f TEXT     The file path to process. Accepted formats: gpx
        --out, -o TEXT      Accepted formats: json
        --indent, -i TEXT   Optionally add indentation level to json. Defaults to None.

    Args:
        inputfile (Path): The input GPX file or directory to process.
        outputfile (Optional[Path]): The output JSON file for file processing mode.
        indentation (Optional[int]): The indentation level for the JSON output. Defaults to None.
    """
    try:
        if len(inputs) == 1 and inputs[0].is_dir():
            inputdir = inputs[0]
            outputdir = output or inputdir / "coordextract_output"
            asyncio.run(
                process_directory(inputdir, outputdir, indentation, concurrency)
            )
        else:
            if len(inputs) == 1:
                inputfile = inputs[0]
                asyncio.run(process(inputfile, output, indentation, concurrency))
            else:
                outputdir = output or Path(".")
                asyncio.run(process_batch(inputs, outputdir, indentation, concurrency))
    except (
        ValueError,
        OSError,
        RuntimeError,
        NotImplementedError,
        ValidationError,
    ) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    app()  # pragma: no cover
