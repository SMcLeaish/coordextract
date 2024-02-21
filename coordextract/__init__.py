"""This module provides utilities for converting geographic coordinates
and handling geographic data formats. It offers functionality to convert
latitude and longitude to Military Grid Reference System (MGRS)
coordinates, process input files in the GPX format adding MGRS data, and
export data to JSON format with optional indentation.

For users interested in command-line interaction, this package includes a CLI tool. 
See the README or use the `--help` option with the CLI tool for usage instructions and options.


"""

from coordextract.factory import handler_factory

__all__ = ["handler_factory"]
