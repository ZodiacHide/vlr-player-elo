import numpy as np

class playerStats:
    def __init__(self, username, agent, rating, acs, kills, deaths, assists, kast, adr, hsp, fk, fd) -> None:
        self.username = username
        self.agent = agent
        self.rating = rating
        self.acs = acs
        self.kills = kills
        self.deaths = deaths
        self.asssists = assists
        self.kast = kast
        self.adr = adr
        self.hsp = hsp
        self.fk = fk
        self.fd = fd

class teamStats:
    def __init__(self, name, startside, first_half, second_half, players_stats) -> None:
        self.name = name
        self.startside = startside
        self.first_half = first_half
        self.second_half = second_half
        self.player_stats = players_stats

class mapData:
    def __init__(self, winner, loser, map_name, picked_by, map_length, winner_score, loser_score, team_stats) -> None:
        self.winner = winner
        self.loser = loser
        self.map_name = map_name
        self.picked_by = picked_by
        self.map_length = map_length
        self.winner_score = winner_score
        self.loser_score = loser_score
        self.team_stats = team_stats

class gameSeries:
    def __init__(self, event_name, time_of_series, teams, scoreline, format, num_maps, vods, maps_data) -> None:
        self.event_name = event_name
        self.time_of_series = time_of_series
        self.teams = teams
        self.format = format
        self.scoreline = scoreline
        self.num_maps = num_maps
        self.vods = vods
        self.maps_data = maps_data
    
player_dtype = np.dtype([
    ('player_name', 'U50'),  # Unicode string, maximum length 50 characters
    ('agent_name', 'U50'),
    ('team_name', 'U50'),
    ('player_data', (float, (12, 3))) # 12x3 array of floats per player
])

team_dtype = np.dtype([
    ('team_name', 'U50'),
    ('starting_side', 'U50'),
    ('first_half', int),
    ('second_half', int)
])

team_data_dtype = np.dtype([
    ('team1_data', team_dtype),
    ('team2_data', team_dtype)
])

map_dtype = np.dtype([
    ('winner_name', 'U50'),
    ('loser_name', 'U50'),
    ('map_name', 'U50'),
    ('team_pick', 'U50'),
    ('map_length', 'U50'),
    ('winner_score', int),
    ('loser_score', int)
])

# Lines 72-82
def find_team_name_side(team):
    '''
    Finds and retrieves name, starting side and div of the left team.
    '''
    name_element = team.find_next('div', class_='team-name').string
    team_name = ' '.join(name_element.split())

    # Span after team_name is always starting side
    team_starting_side_element = name_element.find_next('span')['class'][0]
    team_starting_side = team_starting_side_element.split('-')[-1]

    # Check if team is winner.
    team_won = team.find_next('div')

    return team_name, team_starting_side, team_won

def get_team_ct_t_score(team):
    t_score = int(team.find_next('span', class_='mod-t').get_text())
    ct_score = int(team.find_next('span', class_='mod-ct').get_text())

    return t_score, ct_score
