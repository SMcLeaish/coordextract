
"""
Type Stubs for mgrs.core

This module provides type stubs for the `mgrs.core` package. The actual `mgrs` library does not include
type annotations or a `py.typed` marker, which means static type checkers like `mypy` cannot infer
the types of classes, functions, or methods provided by `mgrs.core`.

The stubs are intended to be a minimal representation, focusing only on the parts of `mgrs.core` that
are actively used, and may need to be extended if additional functionality from the `mgrs` library is
utilized in the future.
"""
from typing import Any

class MGRS:
    def toMGRS(self, latitude: float, longitude: float, *args: Any) -> str:
        """
        Converts latitude and longitude coordinates to an MGRS (Military Grid Reference System) string.

        Args:
            latitude (float): The latitude coordinate to convert.
            longitude (float): The longitude coordinate to convert.
            *args (Any): Additional arguments supported by the MGRS.toMGRS method.

        Returns:
            str: The MGRS string representation of the given latitude and longitude.
        """
        ...

class MGRSError(Exception):
    """
    Exception raised for errors encountered during MGRS conversion operations.
    """
    pass
