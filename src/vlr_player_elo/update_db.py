import sqlite3
import os
from typing import Union
from getters_db import *
from tools.tools import find_data_directory

#############
# TEAM DATA #
#############

# Function to update team name by ID
def update_team_name(team_id:int, new_name:str):
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''UPDATE teams SET name = ?
                    WHERE team_id = ?''', (new_name, team_id))
    conn.commit()
    conn.close()

# Function to update team players by ID
def update_team_name(team_id:int, new_roster:Union[list, tuple]):
    if isinstance(new_roster, tuple):
        new_roster = list(new_roster)
    else:
        raise TypeError(f"'new_roster' must be of type 'list' or 'tuple', but got {type(new_roster).__name__}")
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    team = get_team_by_team_id(team_id=team_id)
    current_roster = sorted(team[2])
    sorted_new_roster = sorted(new_roster)
    
    # Check for same roster
    if sorted_new_roster != current_roster:
        # Find players removed from roster
        removed_players = []
        for i in range(len(current_roster)):
            if sorted_new_roster[i] != current_roster[i]:
                removed_players.append(current_roster[i])
            continue
        
        # Str -> List
        previous_players = team[3].split(", ")
        new_previous_players = removed_players + previous_players

        cursor.execute('''UPDATE teams SET current_roster = ?
                        WHERE team_id = ?''', (sorted_new_roster, team_id))
        cursor.execute('''UPDATE teams SET previous_players = ?
                        WHERE team_id = ?''', (new_previous_players, team_id))
        conn.commit()
        conn.close()

