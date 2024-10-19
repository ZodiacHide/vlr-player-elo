import sqlite3
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
        name TEXT,
        mmr INTEGER DEFAULT NULL,
        maps_played INTEGER DEFAULT 0,
        rounds_played INTEGER DEFAULT 0,
        game_changers INTEGER DEFAULT NULL        
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teams (
        team_id INTEGER PRIMARY KEY,
        team_name TEXT,
        current_roster TEXT,
        previous_players TEXT DEFAULT NULL,
        maps_played INTEGER DEFAULT 0,
        maps_won INTEGER DEFAULT 0,
        series_played INTEGER DEFAULT 0,
        series_won INTEGER DEFAULT 0,
        rounds_played INTEGER DEFAULT 0,
        defence_rounds_won INTEGER DEFAULT 0,
        defence_winp REAL DEFAULT NULL,
        offence_rounds_won INTEGER DEFAULT 0,
        offence_winp REAL DEFAULT NULL,
        abyss_played INTEGER DEFAULT 0,
        abyss_won INTEGER DEFAULT 0,
        ascent_played INTEGER DEFAULT 0,
        ascent_won INTEGER DEFAULT 0,
        bind_played INTEGER DEFAULT 0,
        bind_won INTEGER DEFAULT 0,
        breeze_played INTEGER DEFAULT 0,
        breeze_won INTEGER DEFAULT 0,
        fracture_played INTEGER DEFAULT 0,
        fracture_won INTEGER DEFAULT 0,
        haven_played INTEGER DEFAULT 0,
        haven_won INTEGER DEFAULT 0,
        icebox_played INTEGER DEFAULT 0,
        icebox_won INTEGER DEFAULT 0,
        lotus_played INTEGER DEFAULT 0,
        lotus_won INTEGER DEFAULT 0,
        pearl_played INTEGER DEFAULT 0,
        pearl_won INTEGER DEFAULT 0,
        split_played INTEGER DEFAULT 0,
        split_won INTEGER DEFAULT 0,
        sunset_played INTEGER DEFAULT 0,
        sunset_won INTEGER DEFAULT 0        
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
        game1_id INTEGER,
        game2_id INTEGER DEFAULT NULL,
        game3_id INTEGER DEFAULT NULL,
        game4_id INTEGER DEFAULT NULL,
        game5_id INTEGER DEFAULT NULL,
        FOREIGN KEY (team1_id) REFERENCES teams(team_id),
        FOREIGN KEY (team2_id) REFERENCES teams(team_id),
        FOREIGN KEY (game1_id) REFERENCES games(game_id),
        FOREIGN KEY (game2_id) REFERENCES games(game_id),
        FOREIGN KEY (game3_id) REFERENCES games(game_id),
        FOREIGN KEY (game4_id) REFERENCES games(game_id),
        FOREIGN KEY (game5_id) REFERENCES games(game_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        game_id INTEGER PRIMARY KEY,
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
        game_length TEXT,
        FOREIGN KEY (series_id) REFERENCES series(series_id),
        FOREIGN KEY (team1_id) REFERENCES teams(team_id),
        FOREIGN KEY (team2_id) REFERENCES teams(team_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player_performances (
        performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        player_id INTEGER,
        game_id INTEGER,
        team_id INTEGER,
        agent TEXT,
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
        FOREIGN KEY (game_id) REFERENCES games(game_id),
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