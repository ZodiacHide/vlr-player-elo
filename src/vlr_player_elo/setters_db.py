import sqlite3
import os
from typing import Union
from tools.tools import find_data_directory, assert_parameter_types, write_error_to_file

# Function to insert a player into the database
def insert_player(player_id:int, alias:str, country:Union[str, None], name:Union[str, None], test: bool | None = False) -> None:
    assert_parameter_types(insert_player, player_id, alias, country, name)
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO players (player_id, alias, country, name)
            VALUES (?, ?, ?, ?)
            ''', (player_id, alias, country, name))
            conn.commit()
        except sqlite3.IntegrityError:
            error_string = f"player_id : {player_id}, already exists."
            print(error_string)
            if not test:
                error_string += f' Tried to write: {player_id, alias, country, name}' + '\n'
                write_error_to_file('insert_player_error', error_string)
    finally:
        if conn:
            conn.close()
        else:
            raise ConnectionError(f"Unable to establish connection to {db_path}")

# Function to insert a team into the database
def insert_team(team_id:int, team_name:str, current_roster:str, test: bool | None = False) -> None:
    assert_parameter_types(insert_team, team_id, team_name, current_roster)
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')
    
    vars = [
    team_id,
    team_name,
    current_roster, 
    '',   # previous_players: str
    0,    # maps_played: int
    0,    # maps_won: int
    0,    # series_played: int
    0,    # series_won: int
    0,    # rounds_played: int
    0,    # defence_rounds_won: int
    0.0,  # defence_winp: float
    0,    # offence_rounds_won: int
    0.0,  # offence_winp: float
    0,    # abyss_played: int
    0,    # abyss_won: int
    0,    # ascent_played: int
    0,    # ascent_won: int
    0,    # bind_played: int
    0,    # bind_won: int
    0,    # breeze_played: int
    0,    # breeze_won: int
    0,    # fracture_played: int
    0,    # fracture_won: int
    0,    # haven_played: int
    0,    # haven_won: int
    0,    # icebox_played: int
    0,    # icebox_won: int
    0,    # lotus_played: int
    0,    # lotus_won: int
    0,    # pearl_played: int
    0,    # pearl_won: int
    0,    # split_played: int
    0,    # split_won: int
    0,    # sunset_played: int
    0     # sunset_won: int
    ]

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO teams (team_id, team_name, current_roster, previous_players, maps_played,
                        maps_won, series_played, series_won, rounds_played, defence_rounds_won,
                        defence_winp, offence_rounds_won, offence_winp, abyss_played, abyss_won,
                        ascent_played, ascent_won, bind_played, bind_won, breeze_played, breeze_won,
                        fracture_played, fracture_won, haven_played, haven_won, icebox_played, icebox_won,
                        lotus_played, lotus_won, pearl_played, pearl_won, split_played, split_won,
                        sunset_played, sunset_won)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', vars)
            conn.commit()
        except sqlite3.IntegrityError:
            error_string = f"team_id : {team_id}, already exists."
            print(error_string)
            if not test:
                error_string += f""" Tried to write: {vars}""" + '\n'
                write_error_to_file('insert_team_error', error_string)
    finally:
        if conn:
            conn.close()
        else:
            raise ConnectionError(f"Unable to establish connection to {db_path}")

# Function to insert a series into the database
def insert_series(series_id:int, team1_id:int, team2_id:int, event_name:str, date_played:str, time_started:str,
                  series_format:str, team1_score:int, team2_score:int, map1_id:int, map2_id:int, map3_id:int,
                  map4_id:int, map5_id:int, test: bool | None = False) -> None:
    assert_parameter_types(insert_series, series_id, team1_id, team2_id, event_name, date_played, time_started,
                  series_format, team1_score, team2_score, map1_id, map2_id, map3_id, map4_id, map5_id)
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO series (series_id, team1_id, team2_id, event_name, date_played, time_started,
                        series_format, team1_score, team2_score, map1_id, map2_id, map3_id, map4_id,
                        map5_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (series_id, team1_id, team2_id, event_name, date_played, time_started,
                series_format, team1_score, team2_score, map1_id, map2_id, map3_id, map4_id, map5_id))
            conn.commit()  
        except sqlite3.IntegrityError:
            error_string = f"series_id : {series_id}, already exists."
            print(error_string)
            if not test:
                error_string += f""" Tried to write: {series_id, team1_id, team2_id, event_name, date_played, time_started,
                    series_format, team1_score, team2_score, map1_id, map2_id, map3_id, map4_id, map5_id}""" + '\n'
                write_error_to_file('insert_series_error', error_string)
    finally:
        if conn:
            conn.close()
        else:
            raise ConnectionError(f"Unable to establish connection to {db_path}")
        
# Function to insert a map into the database
def insert_map(map_id:int, series_id:int, map_name:str, picked_by:int, team1_id:int, team1_fh_score:int,
               team1_sh_score:int, team2_id:int, team2_fh_score:int, team2_sh_score:int, pistol_fh_winner:int,
               pistol_sh_winner:int, vod_link:str, map_length:str, test: bool | None = False) -> None:
    assert_parameter_types(insert_map, map_id, series_id, map_name, picked_by, team1_id, team1_fh_score,
                    team1_sh_score, team2_id, team2_fh_score, team2_sh_score, pistol_fh_winner,
                    pistol_sh_winner, vod_link, map_length)
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO maps (map_id, series_id, map_name, picked_by, team1_id, team1_fh_score,
                    team1_sh_score, team2_id, team2_fh_score, team2_sh_score, pistol_fh_winner,
                    pistol_sh_winner, vod_link, map_length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (map_id, series_id, map_name, picked_by, team1_id, team1_fh_score,
                    team1_sh_score, team2_id, team2_fh_score, team2_sh_score, pistol_fh_winner,
                    pistol_sh_winner, vod_link, map_length))
            conn.commit()
        except sqlite3.IntegrityError:
            error_string = f"map_id : {map_id}, already exists."
            print(error_string)
            if not test:
                error_string += f""" Tried to write: {map_id, series_id, map_name, picked_by, team1_id, team1_fh_score,
                        team1_sh_score, team2_id, team2_fh_score, team2_sh_score, pistol_fh_winner,
                        pistol_sh_winner, vod_link, map_length}""" + '\n'
                write_error_to_file('insert_map_error', error_string)
    finally:
        if conn:
            conn.close()
        else:
            raise ConnectionError(f"Unable to establish connection to {db_path}")

# Function to insert a player performance into the database
def insert_player_performance(player_id:int, map_id:int, team_id:int, rating:float, acs:int,
                              kills:int, deaths:int, assists:int, kast:float, adr:float, hsp:float, fk:int, fd:int,
                              test: bool | None = False) -> None:
    assert_parameter_types(insert_player_performance, player_id, map_id, team_id, rating, acs, kills, 
                deaths, assists, kast, adr, hsp, fk, fd)
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try: 
            cursor.execute('''
            INSERT INTO player_performances (performance_id, player_id, map_id, team_id, rating, acs,
                        kills, deaths, assists, kast, adr, hsp, fk, fd)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (player_id, map_id, team_id, rating, acs, kills, 
                deaths, assists, kast, adr, hsp, fk, fd))
            conn.commit()
        except sqlite3.IntegrityError:
            error_string = f"An error occurred."
            print(error_string)
            if not test:
                error_string += f""" Tried to write: {player_id, map_id, team_id, rating, acs, kills, 
                    deaths, assists, kast, adr, hsp, fk, fd}""" + '\n'
                write_error_to_file('insert_player_performance_error', error_string)
    finally:
        if conn:
            conn.close()
        else:
            raise ConnectionError(f"Unable to establish connection to {db_path}")