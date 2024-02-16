from typing import Optional
import asyncio
from typing_extensions import Annotated
import typer
from coordextract.converters import latlon_to_mgrs
from coordextract import filehandler

app = typer.Typer()
async def process_file(inputfile: str, outputfile: Optional[str]):
    filehandler_result = filehandler(inputfile)
    if filehandler_result is not None:
        output = await filehandler_result
        if outputfile:
            print(outputfile)
        else:
            print(output)
    else:
        print("File handler returned None. \
            Please check the input file path or filehandler implementation.")
        raise typer.Exit(code=1)
@app.command()
def main(
    inputfile: Annotated[str, typer.Option(
        "--file", "-f",
        help="The GPX file path to process."
    )] = "",
    coords: Optional[str] = typer.Option(
        None, "--coords", "-c",
        help="A comma-separated latitude and longitude string in quotes for MGRS conversion."
    ),
    outputfile: Optional[str] = typer.Option(
        None, "--out", "-o",
        help="Accepted formats: "
    )
):
    if coords:
        try:
            latitude, longitude = map(float, coords.split(','))
            print(latlon_to_mgrs(latitude, longitude))
        except ValueError as exc:
            print("Invalid latitude and longitude format. \
                Please provide them as quoted comma-separated values.")
            raise typer.Exit(code=1) from exc
    elif inputfile:
        asyncio.run(process_file(inputfile,outputfile))
    else:
        print("No input provided.")
        raise typer.Exit(code=0)

if __name__ == "__main__":
    app()
