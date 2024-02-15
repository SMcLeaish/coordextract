"""
Converters Package

This package provides utilities for converting geographic coordinates between different formats. 
The `latlon_to_mgrs` function is exposed at the package level for easy access, facilitating the 
conversion of latitude and longitude coordinates to their corresponding Military Grid Reference 
System (MGRS) representation.

Usage:
    from coordextract.converters import latlon_to_mgrs
"""
from .latlon_to_mgrs_converter import latlon_to_mgrs
__all__=["latlon_to_mgrs"]
