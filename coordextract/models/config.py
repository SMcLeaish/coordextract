"""
This module contains the ConfigModel class, which is used to load and 
store the configuration data from the config.json file.
"""
from typing import Dict, Optional
import json
from pathlib import Path

from pydantic import BaseModel

class ConfigModel(BaseModel):
    """
    Creates a pydantic model that can be expanded on in the future
    once default values are added to the config.json file. For now 
    creates a remappings dictionary to store user defined key-value
    remaps.
    """
    remappings: Dict[str, str] = {}

    @staticmethod
    def load_config_file(file_path: Path) -> Optional['ConfigModel']:
        """
        Loads the configuration data from the config.json file.
        """
        if file_path.exists() and file_path.is_file():
            with open(file_path, 'r', encoding='utf-8') as file:
                config_data = json.load(file)
                return ConfigModel(**config_data)
        else:
            return None
