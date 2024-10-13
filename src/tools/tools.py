import os
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