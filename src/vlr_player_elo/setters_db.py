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
    
    vars = [team_id, team_name, current_roster]

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO teams (team_id, team_name, current_roster)
            VALUES (?, ?, ?)
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
### FIX THIS, NEED TO CHANGE FOR DEFAULT VALUES ###
def insert_series(series_id:int, team1_id:int, team2_id:int, event_name:str, date_played:str, time_started:str,
                  series_format:str, team1_score:int, team2_score:int, game1_id:int, game2_id:int, game3_id:int,
                  game4_id:int, game5_id:int, test: bool | None = False) -> None:
    assert_parameter_types(insert_series, series_id, team1_id, team2_id, event_name, date_played, time_started,
                  series_format, team1_score, team2_score, game1_id, game2_id, game3_id, game4_id, game5_id)
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO series (series_id, team1_id, team2_id, event_name, date_played, time_started,
                        series_format, team1_score, team2_score, game1_id, game2_id, game3_id, game4_id,
                        game5_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (series_id, team1_id, team2_id, event_name, date_played, time_started,
                series_format, team1_score, team2_score, game1_id, game2_id, game3_id, game4_id, game5_id))
            conn.commit()  
        except sqlite3.IntegrityError:
            error_string = f"series_id : {series_id}, already exists."
            print(error_string)
            if not test:
                error_string += f""" Tried to write: {series_id, team1_id, team2_id, event_name, date_played, time_started,
                    series_format, team1_score, team2_score, game1_id, game2_id, game3_id, game4_id, game5_id}""" + '\n'
                write_error_to_file('insert_series_error', error_string)
    finally:
        if conn:
            conn.close()
        else:
            raise ConnectionError(f"Unable to establish connection to {db_path}")
        
# Function to insert a game into the database
def insert_game(game_id:int, series_id:int, map_name:str, picked_by:int, team1_id:int, team1_fh_score:int,
               team1_sh_score:int, team2_id:int, team2_fh_score:int, team2_sh_score:int, pistol_fh_winner:int,
               pistol_sh_winner:int, vod_link:str, game_length:str, test: bool | None = False) -> None:
    assert_parameter_types(insert_game, game_id, series_id, map_name, picked_by, team1_id, team1_fh_score,
                    team1_sh_score, team2_id, team2_fh_score, team2_sh_score, pistol_fh_winner,
                    pistol_sh_winner, vod_link, game_length)
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO games (game_id, series_id, map_name, picked_by, team1_id, team1_fh_score,
                    team1_sh_score, team2_id, team2_fh_score, team2_sh_score, pistol_fh_winner,
                    pistol_sh_winner, vod_link, game_length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (game_id, series_id, map_name, picked_by, team1_id, team1_fh_score,
                    team1_sh_score, team2_id, team2_fh_score, team2_sh_score, pistol_fh_winner,
                    pistol_sh_winner, vod_link, game_length))
            conn.commit()
        except sqlite3.IntegrityError:
            error_string = f"game_id : {game_id}, already exists."
            print(error_string)
            if not test:
                error_string += f""" Tried to write: {game_id, series_id, map_name, picked_by, team1_id, team1_fh_score,
                        team1_sh_score, team2_id, team2_fh_score, team2_sh_score, pistol_fh_winner,
                        pistol_sh_winner, vod_link, game_length}""" + '\n'
                write_error_to_file('insert_map_error', error_string)
    finally:
        if conn:
            conn.close()
        else:
            raise ConnectionError(f"Unable to establish connection to {db_path}")

# Function to insert a player performance into the database
def insert_player_performance(player_id:int, game_id:int, team_id:int, agent:str, rating:float, acs:int,
                              kills:int, deaths:int, assists:int, kast:float, adr:int, hsp:float, fk:int, fd:int,
                              test: bool | None = False) -> None:
    assert_parameter_types(insert_player_performance, player_id, game_id, team_id, agent, rating, acs, kills, 
                deaths, assists, kast, adr, hsp, fk, fd)
    # Path to the db
    db_path = os.path.join(find_data_directory(), 'valorant.db')

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try: 
            cursor.execute('''
            INSERT INTO player_performances (player_id, game_id, team_id, agent, rating, acs,
                        kills, deaths, assists, kast, adr, hsp, fk, fd)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (player_id, game_id, team_id, agent, rating, acs, kills, 
                deaths, assists, kast, adr, hsp, fk, fd))
            conn.commit()
        except sqlite3.IntegrityError:
            error_string = f"An error occurred."
            print(error_string)
            if not test:
                error_string += f""" Tried to write: {player_id, game_id, team_id, agent, rating, acs, kills, 
                    deaths, assists, kast, adr, hsp, fk, fd}""" + '\n'
                write_error_to_file('insert_player_performance_error', error_string)
    finally:
        if conn:
            conn.close()
        else:
            raise ConnectionError(f"Unable to establish connection to {db_path}")