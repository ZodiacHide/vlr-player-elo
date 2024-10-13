import sqlite3

###############
# PLAYER DATA #
###############

# Function to fetch player data by ID
def get_player(player_id:int) -> tuple:
    conn = sqlite3.connect('valorant.db')
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
    conn = sqlite3.connect('valorant.db')
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
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM series 
                   WHERE series_id = ?''', (series_id,))
    series = cursor.fetchone()
    conn.close()
    return series

# Function to fetch series data by team ID
def get_series_by_team_id(team_id:int) -> tuple:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM series WHERE ? IN 
                   (team1_id, team2_id)''', (team_id,))
    series = cursor.fetchone()
    conn.close()
    return series

# Function to fetch series data by team ID
def get_series_by_map_id(map_id:int) -> tuple:
    conn = sqlite3.connect('valorant.db')
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
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM maps 
                   WHERE map_id = ?''', (map_id,))
    map = cursor.fetchone()
    conn.close()
    return map

# Function to fetch map data by series ID
def get_map_by_series_id(series_id:int) -> tuple:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM maps 
                   WHERE series_id = ?''', (series_id,))
    map = cursor.fetchone()
    conn.close()
    return map

# Function to fetch map data by series ID
def get_map_by_team_id(team_id:int) -> tuple:
    conn = sqlite3.connect('valorant.db')
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
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM player_performances 
                   WHERE performance_id = ?''', (performance_id,))
    performance = cursor.fetchone()
    conn.close()
    return performance

# Function to fetch player performance data by player ID
def get_player_performance_by_player_id(player_id:int) -> tuple:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM player_performances 
                   WHERE player_id = ?''', (player_id,))
    performance = cursor.fetchone()
    conn.close()
    return performance

# Function to fetch player performance data by map ID
def get_player_performance_by_map_id(map_id:int) -> tuple:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM player_performances 
                   WHERE map_id = ?''', (map_id,))
    performance = cursor.fetchone()
    conn.close()
    return performance

# Function to fetch player performance data by team ID
def get_player_performance_by_team_id(team_id:int) -> tuple:
    conn = sqlite3.connect('valorant.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM player_performances 
                   WHERE team_id = ?''', (team_id,))
    performance = cursor.fetchone()
    conn.close()
    return performance