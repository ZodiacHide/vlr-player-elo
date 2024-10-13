import os
import sqlite3
from typing import Optional

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