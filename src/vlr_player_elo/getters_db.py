import sqlite3

# Function to fetch player data by ID
def get_player(player_id):
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players WHERE player_id = ?', (player_id,))
    player = cursor.fetchone()
    conn.close()
    return player

# Function to fetch series data by ID
def get_series(series_id):
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM series WHERE series_id = ?', (series_id,))
    series = cursor.fetchone()
    conn.close()
    return series