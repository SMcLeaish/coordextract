# coordextract
coordextract is a Python library and CLI tool for converting data from 
GPX files into pydantic models for further processesing. It was designed 
to be used as a FastAPI service. 

While building the pydantic model it verifies that the points are legitimate 
and does MGRS conversion which is added to the model as a new field.

The CLI tool will output the model as a JSON string or file. 

## Features

- Batch process GPX files asynchronously with asyncio.
- Use CPU concurrency if datasets are large.
- Command-line interface (CLI).

## Installation
coordextract uses Poetry for dependency management.
[Poetry website](https://python-poetry.org/docs/)
```shell
git clone https://github.com/SMcLeaish/coordextract/
cd coordextract
poetry install
```
### As a library

The main entry point for the library is the CoordExtract.process_coords()
```python
from coordextract import process_coords

"""process_coords() takes five arguments:
    - input_file(s): Path - The path to the input GPX file(s).
    - output_file: Optional(Path) - The path to the output file.
    - indent: Optional(int) - The number of spaces to indent JSON output. 
        Default 2.
    - concurrency: Optional(bool) - Will attempt to spawn multiple processes
        for batch requests. Default False.
    - context: Optional(str) - If None a the PointModel will be returned. 
        If set to cli, output will be JSON to stdout if no output file is 
        specified. Default None.
"""
process_coords('path/to/file.gpx', 'path/to/output.csv', 2, True, 'cli')
```

### As a CLI tool

coordextract on the command line takes gpx file(s) as its first input and
supports the following options:

`--output-file` - The path to the output file.

`--indent` - The number of spaces to indent JSON output. Default 2.

`--concurrency` - Will attempt to spawn multiple processes for batch requests.

`--help` - Display the help message.

### License

This project is licensed under the MIT License - see the LICENSE file for details.

 *This repository is mirrored at [https://github.com/SMcLeaish/coordextract/](https://github.com/SMcLeaish/coordextract/) 
from [https://gitlab.com/smcleaish/coordextract](https://gitlab.com/smcleaish/coordextract) and uses gitlab CI*
