"""
Initializes the model factory module, providing functions to generate geographic data models from 
various file types.

Currently includes functionality for processing GPX files into point models. This module aims to 
serve as a centralized location for functions that convert file-based geographic data into 
structured models, facilitating easy expansion to support additional file formats in the future.

Available Functions:
- process_gpx_to_point_models: Converts GPX file data into a list of PointModel instances.
"""

from coordextract.factory.gpx_model_builder import process_gpx_to_point_models

__all__ = ["process_gpx_to_point_models"]
