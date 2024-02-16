# coordextract
coordextract is a Python library and CLI tool for converting latitude and longitude data from GPX files into Military Grid Reference System (MGRS) coordinates. The library parses GPX files, extracts geographical points, and provides an efficient way to convert and export these points into various formats.

## Features

- Parse GPX files to extract latitude and longitude data.
- Convert latitude and longitude to MGRS coordinates.
- Output the converted data in CSV, JSON, or XLSX formats (coming soon).
- Command-line interface (CLI).

## Installation

To install coordextract, run the following command:

```shell
pip install coordextract
```

## Usage

You can use coordextract as a library by importing it, or as a standalone CLI tool.

### As a library

```python
from coordextract import filehandler

# Parse a GPX file and return a list of pydantic model objects
points = filehandler('path/to/your/file.gpx')
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

### License

This project is licensed under the MIT License - see the LICENSE file for details.

 *This repository is mirrored at [https://github.com/SMcLeaish/coordextract/](https://github.com/SMcLeaish/coordextract/) from [https://gitlab.com/smcleaish/coordextract](https://gitlab.com/smcleaish/coordextract) and uses gitlab CI*
