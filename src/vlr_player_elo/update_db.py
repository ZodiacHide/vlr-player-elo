import sqlite3
import os
from typing import Union
from vlr_player_elo.getters_db import *
from tools.tools import find_data_directory, validate_map_name, assert_parameter_types

#############
# TEAM DATA #
#############

# Function to update team name by ID
def update_team_name(team_id:int, new_name:str):
    assert_parameter_types(update_team_name, team_id, new_name)
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''UPDATE teams SET name = ?
                            WHERE team_id = ?''', (new_name, team_id))
            conn.commit()
        except Exception as e:
            print(f"Unexpected error: {e}")
            conn.rollback()
    finally:
        if conn:
            conn.close()
        else:
            raise ConnectionError(f"Unable to establish connection to {db_path}")

# Function to update team roster by ID
def update_team_roster(team_id:int, new_roster:Union[list, tuple]):
    assert_parameter_types(update_team_roster, team_id, new_roster)
    new_roster = list(new_roster)
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        team = get_team_by_team_id(team_id=team_id)
        current_roster = sorted(team[2].split(', '))
        sorted_new_roster = sorted(new_roster)

        # Check for same roster
        if sorted_new_roster != current_roster:
            # Find players removed from roster
            removed_players = []
            for active_player in current_roster:
                removed_player_confidence = 0
                for new_player in sorted_new_roster:
                    if active_player != new_player:
                        removed_player_confidence += 1
                    else:
                        continue
                if removed_player_confidence == len(sorted_new_roster):
                    removed_players.append(active_player)
            sorted_new_roster = ', '.join(sorted_new_roster)

            # Str -> List
            previous_players = team[3].split(", ")
            # Handle empty list entry
            if previous_players[-1] != '':
                new_previous_players = removed_players + previous_players
            new_previous_players = removed_players + previous_players[:-1]
            new_previous_players = ', '.join(new_previous_players)
            try:
                cursor.execute('''UPDATE teams SET current_roster = ?
                                WHERE team_id = ?''', (sorted_new_roster, team_id))
                cursor.execute('''UPDATE teams SET previous_players = ?
                                WHERE team_id = ?''', (new_previous_players, team_id))
                conn.commit()
            except Exception as e:
                print(f"Unexpected error: {e}")
                conn.rollback()
    finally:
        if conn:
            conn.close()
        else:
            raise ConnectionError(f"Unable to establish connection to {db_path}")

def update_map_stat(team_id:int, map_name:str, map_won:bool):
    assert_parameter_types(update_map_stat, team_id, map_name, map_won)
    assert validate_map_name(map_name)
    map_name = map_name.lower()
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')
    try: 
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            if map_won:
                # Update map win count
                cursor.execute(f'''UPDATE teams SET {map_name}_won = {map_name}_won + 1
                                WHERE team_id = ?''', (team_id,))
                # Update total map win count
                cursor.execute(f'''UPDATE teams SET maps_won = maps_won + 1
                                WHERE team_id = ?''', (team_id,))
            # Update map played count
            cursor.execute(f'''UPDATE teams SET {map_name}_played = {map_name}_played + 1
                            WHERE team_id = ?''', (team_id,))
            # Update total map played count
            cursor.execute(f'''UPDATE teams SET maps_played = maps_played + 1
                                WHERE team_id = ?''', (team_id,))
            conn.commit()
        except Exception as e:
            print(f"Unexpected error: {e}")
            conn.rollback()
    finally:
        if conn:
            conn.close()
        else:
            raise ConnectionError(f"Unable to establish connection to {db_path}")