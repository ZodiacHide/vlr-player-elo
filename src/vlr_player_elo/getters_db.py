import sqlite3
import os
from tools.tools import find_data_directory

###############
# PLAYER DATA #
###############

# Function to fetch player data by ID
def get_player(player_id:int) -> tuple:
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM players 
                   WHERE player_id = ?''', (player_id,))
    player = cursor.fetchone()
    conn.close()
    return player

#############
# TEAM DATA #
#############

# Function to fetch team data by team ID
def get_team_by_team_id(team_id:int) -> tuple:
    """
    ## Returns
        **team** : *tuple*
        Tuple containing datapoints for team_id:

        ### Identification:
        - 0  : *int*    : team_id
        - 1  : *str*    : team_name

        ### Roster:
        - 2  : *str*    : current_roster
        - 3  : *str*    : previous_players

        ### Match Statistics:
        - 4  : *int*    : maps_played
        - 5  : *int*    : maps_won
        - 6  : *int*    : series_played
        - 7  : *int*    : series_won
        - 8  : *int*    : rounds_played
        - 9  : *int*    : defence_rounds_won
        - 10 : *float*  : defence_winp
        - 11 : *int*    : offence_rounds_won
        - 12 : *float*  : offence_winp

        ### Map Specific Statistics:
        - 13 : *int*    : abyss_played
        - 14 : *int*    : abyss_won
        - 15 : *int*    : ascent_played
        - 16 : *int*    : ascent_won
        - 17 : *int*    : bind_played
        - 18 : *int*    : bind_won
        - 19 : *int*    : breeze_played
        - 20 : *int*    : breeze_won
        - 21 : *int*    : fracture_played
        - 22 : *int*    : fracture_won
        - 23 : *int*    : haven_played
        - 24 : *int*    : haven_won
        - 25 : *int*    : icebox_played
        - 26 : *int*    : icebox_won
        - 27 : *int*    : lotus_played
        - 28 : *int*    : lotus_won
        - 29 : *int*    : pearl_played
        - 30 : *int*    : pearl_won
        - 31 : *int*    : split_played
        - 32 : *int*    : split_won
        - 33 : *int*    : sunset_played
        - 34 : *int*    : sunset_won"""
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM teams 
                   WHERE team_id = ?''', (team_id,))
    team = cursor.fetchone()
    conn.close()
    return team

###############
# SERIES DATA #
###############

# Function to fetch series data by series ID
def get_series_by_series_id(series_id:int) -> tuple:
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM series 
                   WHERE series_id = ?''', (series_id,))
    series = cursor.fetchone()
    conn.close()
    return series

# Function to fetch series data by team ID
def get_series_by_team_id(team_id:int) -> tuple:
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM series WHERE ? IN 
                   (team1_id, team2_id)''', (team_id,))
    series = cursor.fetchone()
    conn.close()
    return series

# Function to fetch series data by team ID
def get_series_by_map_id(map_id:int) -> tuple:
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM series WHERE ? IN 
                   (map1_id, map2_id, map3_id, map4_id, 
                   map5_id)''', (map_id,))
    series = cursor.fetchone()
    conn.close()
    return series

############
# MAP DATA #
############

# Function to fetch map data by map ID
def get_map_by_map_id(map_id:int) -> tuple:
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM maps 
                   WHERE map_id = ?''', (map_id,))
    map = cursor.fetchone()
    conn.close()
    return map

# Function to fetch map data by series ID
def get_map_by_series_id(series_id:int) -> tuple:
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM maps 
                   WHERE series_id = ?''', (series_id,))
    map = cursor.fetchone()
    conn.close()
    return map

# Function to fetch map data by series ID
def get_map_by_team_id(team_id:int) -> tuple:
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM maps WHERE ? IN 
                   (team1_id, team2_id)''', (team_id,))
    map = cursor.fetchone()
    conn.close()
    return map

####################
# PERFORMANCE DATA #
####################

# Function to fetch player performance data by ID
def get_player_performance_by_performance_id(performance_id:int) -> tuple:
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM player_performances 
                   WHERE performance_id = ?''', (performance_id,))
    performance = cursor.fetchone()
    conn.close()
    return performance

# Function to fetch player performance data by player ID
def get_player_performance_by_player_id(player_id:int) -> tuple:
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM player_performances 
                   WHERE player_id = ?''', (player_id,))
    performance = cursor.fetchone()
    conn.close()
    return performance

# Function to fetch player performance data by map ID
def get_player_performance_by_map_id(map_id:int) -> tuple:
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM player_performances 
                   WHERE map_id = ?''', (map_id,))
    performance = cursor.fetchone()
    conn.close()
    return performance

# Function to fetch player performance data by team ID
def get_player_performance_by_team_id(team_id:int) -> tuple:
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM player_performances 
                   WHERE team_id = ?''', (team_id,))
    performance = cursor.fetchone()
    conn.close()
    return performance