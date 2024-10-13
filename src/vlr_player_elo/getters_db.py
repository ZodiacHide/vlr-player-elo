import sqlite3

# Function to fetch player data by ID
def get_player(player_id:int) -> tuple:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players WHERE player_id = ?', (player_id,))
    player = cursor.fetchone()
    conn.close()
    return player

# Function to fetch team data by ID
def get_team(team_id:int) -> tuple:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM teams WHERE team_id = ?', (team_id,))
    team = cursor.fetchone()
    conn.close()
    return team

# Function to fetch series data by ID
def get_series(series_id:int) -> tuple:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM series WHERE series_id = ?', (series_id,))
    series = cursor.fetchone()
    conn.close()
    return series

# Function to fetch map data by ID
def get_map(map_id:int) -> tuple:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM maps WHERE map_id = ?', (map_id,))
    map = cursor.fetchone()
    conn.close()
    return map

# Function to fetch player performance data by ID
def get_player_performance(performance_id:int) -> tuple:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM player_performances WHERE performance_id = ?', (performance_id,))
    performance = cursor.fetchone()
    conn.close()
    return performance