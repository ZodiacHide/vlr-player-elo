import sqlite3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from tools.tools import find_data_directory

# Function to initialize the database and create tables
def init_db():
    db_dir = find_data_directory()
    conn = sqlite3.connect(db_dir + '/valorant.db')
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        player_id INTEGER PRIMARY KEY,
        alias TEXT,
        country TEXT,
        name TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        team_id INTEGER PRIMARY KEY,
        team_name TEXT,
        current_roster TEXT,
        previous_players TEXT,
        maps_played INTEGER,
        maps_won INTEGER,
        series_played INTEGER,
        series_won INTEGER,
        rounds_played INTEGER,
        defence_rounds_won INTEGER,
        defence_winp REAL,
        offence_rounds_won INTEGER,
        offence_winp REAL,
        abyss_played INTEGER,
        abyss_won INTEGER,
        ascent_played INTEGER,
        ascent_won INTEGER,
        bind_played INTEGER,
        bind_won INTEGER,
        breeze_played INTEGER,
        breeze_won INTEGER,
        fracture_played INTEGER,
        fracture_won INTEGER,
        haven_played INTEGER,
        haven_won INTEGER,
        icebox_played INTEGER,
        icebox_won INTEGER,
        lotus_played INTEGER,
        lotus_won INTEGER,
        pearl_played INTEGER,
        pearl_won INTEGER,
        split_played INTEGER,
        split_won INTEGER,
        sunset_played INTEGER,
        sunset_won INTEGER        
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS series (
        series_id INTEGER PRIMARY KEY,
        team1_id INTEGER,
        team2_id INTEGER,
        event_name TEXT,
        date_played TEXT,
        time_started TEXT,
        series_format TEXT,
        team1_score INTEGER,
        team2_score INTEGER,
        map1_id INTEGER,
        map2_id INTEGER,
        map3_id INTEGER,
        map4_id INTEGER,
        map5_id INTEGER,
        FOREIGN KEY (team1_id) REFERENCES teams(team_id),
        FOREIGN KEY (team2_id) REFERENCES teams(team_id),
        FOREIGN KEY (map1_id) REFERENCES maps(map_id),
        FOREIGN KEY (map2_id) REFERENCES maps(map_id),
        FOREIGN KEY (map3_id) REFERENCES maps(map_id),
        FOREIGN KEY (map4_id) REFERENCES maps(map_id),
        FOREIGN KEY (map5_id) REFERENCES maps(map_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS maps (
        map_id INTEGER PRIMARY KEY,
        series_id INTEGER,
        map_name TEXT,
        picked_by INTEGER,
        team1_id INTEGER,
        team1_fh_score INTEGER,
        team1_sh_score INTEGER,
        team2_id INTEGER,
        team2_fh_score INTEGER,
        team2_sh_score INTEGER,
        pistol_fh_winner INTEGER,
        pistol_sh_winner INTEGER,
        vod_link TEXT,
        map_length TEXT,
        FOREIGN KEY (series_id) REFERENCES series(series_id),
        FOREIGN KEY (team1_id) REFERENCES teams(team_id),
        FOREIGN KEY (team2_id) REFERENCES teams(team_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_performances (
        performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER,
        map_id INTEGER,
        team_id INTEGER,
        rating REAL,
        acs INTEGER,
        kills INTEGER,
        deaths INTEGER,
        assists INTEGER,
        kast REAL,
        adr REAL,
        hsp REAL,
        fk INTEGER,
        fd INTEGER,
        FOREIGN KEY (player_id) REFERENCES players(player_id),
        FOREIGN KEY (map_id) REFERENCES maps(map_id),
        FOREIGN KEY (team_id) REFERENCES teams(team_id)
    )
    ''')

    conn.commit()
    conn.close()

def main():
    # Initialize the database
    init_db()
    
if __name__=='__main__':
    main()