from typing import Optional
import logging
import asyncio
from typing_extensions import Annotated
import typer
from coordextract.converters import latlon_to_mgrs
from coordextract.exporters import point_models_to_json
from coordextract import filehandler

app = typer.Typer()


async def process_file(
    inputfile: str, outputfile: Optional[str], indentation: Optional[int]
):
    filehandler_result = filehandler(inputfile)
    if filehandler_result is not None:
        output = await filehandler_result
        point_models_to_json(output, outputfile, indentation)
        raise typer.Exit(code=0)
    logging.error(
        "File handler returned None. \
        Please check the input file path or filehandler implementation."
    )
    raise typer.Exit(code=1)


@app.command()
def main(
    inputfile: Annotated[
        str,
        typer.Option(
            "--file", "-f", help="The file path to process. Accepted formats: gpx"
        ),
    ] = "",
    coords: Optional[str] = typer.Option(
        None,
        "--coords",
        "-c",
        help="A comma-separated latitude and longitude string in quotes for MGRS conversion.",
    ),
    outputfile: Optional[str] = typer.Option(
        None, "--out", "-o", help="Accepted formats: json "
    ),
    indentation: Optional[int] = typer.Option(
        None,
        "--indent",
        "-i",
        help="Optionally add indentation level to json. Defaults to 2.",
    ),
):
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
