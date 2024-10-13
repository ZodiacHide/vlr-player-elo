import sqlite3

# Function to insert a player into the database
def insert_player(player_id:int, alias:str, country:str, name:str) -> None:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO players (player_id, alias, country, name)
    VALUES (?, ?, ?, ?)
    ''', (player_id, alias, country, name))
    conn.commit()
    conn.close()

# Function to insert a team into the database
def insert_team(team_id:int, team_name:str, current_roster:str, previous_players:str, maps_played:int,
                  maps_won:int, series_played:int, series_won:int, rounds_played:int, defence_rounds_won:int,
                  defence_winp:float, offence_rounds_won:int, offence_winp:float, abyss_played:int, abyss_won:int,
                  ascent_played:int, ascent_won:int, bind_played:int, bind_won:int, breeze_played:int, breeze_won:int,
                  fracture_played:int, fracture_won:int, haven_played:int, haven_won:int, icebox_played:int, icebox_won:int,
                  lotus_played:int, lotus_won:int, pearl_played:int, pearl_won:int, split_played:int, split_won:int,
                  sunset_played:int, sunset_won:int) -> None:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO teams (team_id, team_name, current_roster, previous_players, maps_played,
                  maps_won, series_played, series_won, rounds_played, defence_rounds_won,
                  defence_winp, offence_rounds_won, offence_winp, abyss_played, abyss_won,
                  ascent_played, ascent_won, bind_played, bind_won, breeze_played, breeze_won,
                  fracture_played, fracture_won, haven_played, haven_won, icebox_played, icebox_won,
                  lotus_played, lotus_won, pearl_played, pearl_won, split_played, split_won,
                  sunset_played, sunset_won)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (team_id, team_name, current_roster, previous_players, maps_played,
                  maps_won, series_played, series_won, rounds_played, defence_rounds_won,
                  defence_winp, offence_rounds_won, offence_winp, abyss_played, abyss_won,
                  ascent_played, ascent_won, bind_played, bind_won, breeze_played, breeze_won,
                  fracture_played, fracture_won, haven_played, haven_won, icebox_played, icebox_won,
                  lotus_played, lotus_won, pearl_played, pearl_won, split_played, split_won,
                  sunset_played, sunset_won))
    conn.commit()
    conn.close()

# Function to insert a series into the database
def insert_series(series_id:int, team1_id:int, team2_id:int, event_name:str, date_played:str, time_started:str,
                  series_format:str, team1_score:int, team2_score:int, map1_id:int, map2_id:int, map3_id:int,
                  map4_id:int, map5_id:int) -> None:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO series (series_id, team1_id, team2_id, event_name, date_played, time_started,
                   series_format, team1_score, team2_score, map1_id, map2_id, map3_id, map4_id,
                   map5_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (series_id, team1_id, team2_id, event_name, date_played, time_started,
          series_format, team1_score, team2_score, map1_id, map2_id, map3_id, map4_id, map5_id))
    conn.commit()
    conn.close()

# Function to insert a map into the database
## MAYBE CHANGE PICKED_BY TO INTEGER ID ##
## MAYBE CHANGE PISTOL WINNER TO INTEGER ID ##
def insert_map(map_id:int, series_id:int, map_name:str, picked_by:str, team1_id:int, team1_fh_score:int,
               team1_sh_score:int, team2_id:int, team2_fh_score:int, team2_sh_score:int, pistol_fh_winner:str,
               pistol_sh_winner:str, vod_link:str, map_length:str) -> None:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO maps (map_id, series_id, map_name, picked_by, team1_id, team1_fh_score,
               team1_sh_score, team2_id, team2_fh_score, team2_sh_score, pistol_fh_winner,
               pistol_sh_winner, vod_link, map_length)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (map_id, series_id, map_name, picked_by, team1_id, team1_fh_score,
               team1_sh_score, team2_id, team2_fh_score, team2_sh_score, pistol_fh_winner,
               pistol_sh_winner, vod_link, map_length))
    conn.commit()
    conn.close()

# Function to insert a player performance into the database
def insert_player_performance(performance_id:int, player_id:int, map_id:int, team_id:int, rating:float, acs:int,
                              kills:int, deaths:int, assists:int, kast:float, adr:float, hsp:float, fk:int, fd:int) -> None:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO player_performances (performance_id, player_id, map_id, team_id, rating, acs,
                kills, deaths, assists, kast, adr, hsp, fk, fd)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (performance_id, player_id, map_id, team_id, rating, acs,
                kills, deaths, assists, kast, adr, hsp, fk, fd))
    conn.commit()
    conn.close()