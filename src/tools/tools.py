import os
import sqlite3
import inspect
from typing import Optional, Callable

def find_data_directory(start_dir: Optional[str] = os.path.dirname(os.path.abspath(__file__))) -> str:
    current_dir = start_dir
    while True:
        # Check if the data directory exists in the current directory
        potential_data_dir = os.path.join(current_dir, 'data')
        if os.path.isdir(potential_data_dir):
            return potential_data_dir

        # Move up to the parent directory
        parent_dir = os.path.dirname(current_dir)
        
        # If we have reached the root directory, stop
        if parent_dir == current_dir:
            raise FileNotFoundError("The data directory was not found in the directory tree.")
        
        current_dir = parent_dir

def delete_row(table_name:str, index_name:str, index_value):
    if not isinstance(table_name, str):
        raise TypeError(f"'table_name' must be of type 'str', but got {type(table_name).__name__}")
    if not isinstance(index_name, str):
        raise TypeError(f"'index_name' must be of type 'str', but got {type(index_name).__name__}")
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE {index_name} = ?", (index_value,))
        conn.commit()
    finally:
        # Close the connection
        if conn:
            conn.close()

def validate_map_name(map_name:str):
    assert isinstance(map_name, str), f"'map_name' must be of type 'str', but got {type(map_name).__name__}"
    map_name = map_name.lower()
    VALID_MAP_NAMES = {
    "abyss", "ascent", "bind", "breeze", "fracture", 
    "haven", "icebox", "lotus", "pearl", "split", "sunset"
    }
    assert map_name in VALID_MAP_NAMES, f"Invalid map name '{map_name}'. Must be one of {', '.join(VALID_MAP_NAMES)}"
    return True

def _fetch_parameter_types(func:Callable):
    signature = inspect.signature(func)
    param_types = {param_name: param.annotation for param_name, param in signature.parameters.items()}
    return param_types

def assert_parameter_types(func:Callable, *args, **kwargs):
    assert isinstance(func, Callable), f"'func' must be callable, but is instead {type(func).__name__}"
    param_types = _fetch_parameter_types(func)
    if list(param_types.keys())[-1] == 'test':
        param_types.popitem()
    params = list(args) + list(kwargs.values())
    param_names = list(param_types.keys())

    assert len(params) == len(param_types), f"Expected {len(param_types)} parameters, but got {len(params)}"

    for i, param in enumerate(params):
        param_name = param_names[i]
        expected_type = param_types[param_name]
        actual_type = type(param)
        assert isinstance(param, expected_type), f"'{param_name}' must be of type '{expected_type.__name__}', but got '{actual_type.__name__}'"
