# coordextract
coordextract is a Python library and CLI tool for converting latitude and longitude data from GPX files into Military Grid Reference System (MGRS) coordinates. The library parses GPX files, extracts geographical points, and provides an efficient way to convert and export these points into various formats.

## Features

- Parse GPX files to extract latitude and longitude data 
- Convert latitude and longitude to MGRS coordinates.
- Output the converted JSON
- Command-line interface (CLI).

## Installation
coordextract uses Poetry for dependency management. To install coordextract, first ensure you have Poetry installed. If not, you can install Poetry by following the instructions on the [Poetry website](https://python-poetry.org/docs/).

Once Poetry is installed, you can install coordextract by cloning the repository and using Poetry:

```shell
git clone https://github.com/SMcLeaish/coordextract/
cd coordextract
poetry install
```

## Usage

You can use coordextract as a library by importing it, or as a standalone CLI tool.

### As a library

```python
inputhandler(filename: Path) -> list[PointModel]:
outputhandler(point_models: list[PointModel], filename: Optional[Path], indentation: Optional[int]
```

### As a CLI tool


```shell
coordextract -f 'path/to/your/file.gpx'
```
### CLI options

* -f / --file TEXT: The GPX file path to process.
* -c / --coords TEXT: A comma-separated latitude and longitude string for MGRS conversion. (Default: None)
* -o / --out TEXT: Specify the output format and destination. (Accepted formats: csv, json, xlsx) (Default: None)
* --install-completion: Install completion for the current shell.
* --show-completion: Show completion for the current shell, to copy it or customize the installation.
* --help: Show help message and exit.

### Dependencies

Install development dependencies with: 
`pip install -r requirements.txt`

### QA

Testing, linting, and type checking are performed with pytest, pylint, and mypy respectively. To run these checks, use the following commands:

```shell
pytest
pylint coordextract
mypy coordextract
```

### Formatting
This project uses Black for code formatting to ensure a consistent code style. To format your code, run:
```shell
poetry run black .
```

### License

This project is licensed under the MIT License - see the LICENSE file for details.

 *This repository is mirrored at [https://github.com/SMcLeaish/coordextract/](https://github.com/SMcLeaish/coordextract/) from [https://gitlab.com/smcleaish/coordextract](https://gitlab.com/smcleaish/coordextract) and uses gitlab CI*
