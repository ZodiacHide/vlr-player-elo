import bs4
import numpy as np
import os

def find_team_name_side(team: bs4.element.Tag) -> tuple:
    '''
    Finds and retrieves name and starting side for a team.

    Args:
        team (bs4.element.Tag): Beautiful soup div tag of the team.

    Returns:
        str: Scorelines for Attack side and Defender side.
    '''
    name_element = team.find_next('div', class_='team-name').string
    team_name = ' '.join(name_element.split())

    # Span after team_name is always starting side
    team_starting_side_element = name_element.find_next('span')['class'][0]
    team_starting_side = team_starting_side_element.split('-')[-1]

    return team_name, team_starting_side

def get_team_ct_t_score(team: bs4.element.Tag) -> tuple:
    '''
    Finds and retrieves scorelines from both halves for a team.

    Args:
        team (bs4.element.Tag): Beautiful soup tag of the team.

    Returns:
        str: Scorelines for Attack side and Defender side.
    '''
    try:
        score_div = team.find_next('span', class_='mod-ct')
        t_score = int(team.find_next('span', class_='mod-t').get_text())
        ct_score = int(team.find_next('span', class_='mod-ct').get_text())
    except:
        final_score = team.find('div', style='margin-right: 12px;')
        if final_score != None:
            ct_score = final_score.get_text()
            t_score = 0
        else:
            final_score = team.find('div', style='margin-left: 8px;')
            ct_score = final_score.get_text()
            t_score = 0
        
    # Check if map went to OT, handle if it didn't
    try:
        ot_score = int(score_div.find_next_sibling('span', class_='mod-ot').get_text())
    except AttributeError:
        ot_score = 0

    return t_score, ct_score, ot_score

def write_player_data_to_file(player_data: dict, team_name: str, maps: list, 
                              scoreline: str, team_a_name: str, team_b_name: str
                              ) -> None:
    player_name = player_data['player_name']
    map_count = int(scoreline[0]) + int(scoreline[-1])
    path = f'players\{player_name}.txt'
    # Retrieve player data for each map #
    map_data = []
    for i, map in enumerate(player_data['matches']):
        # Skip default stats
        if i > map_count-1:
            continue
        map_stats = list(map.values())
        map_data.extend([map_stats])
    
    ## MAKE FUNC ##
    # Make array of wins/losses for player
    map_results = np.zeros(map_count, dtype=str)
    for i in range(map_count):
        scores = maps[i]['scoreline']
        team_a_score = scores['first_half']['team_a'] + scores['second_half']['team_a'] + scores['overtime']['team_a']
        team_b_score = scores['first_half']['team_b'] + scores['second_half']['team_b'] + scores['overtime']['team_b']
        if team_a_score > team_b_score:
            if team_name == team_a_name:
                map_results[i] = 'W'
            else:
                map_results[i] = 'L'
        else:
            if team_name == team_b_name:
                map_results[i] = 'W'
            else:
                map_results[i] = 'L'

    if os.path.exists(path):
        # Update file with relevant info
        with open(path, 'a') as infile:
            for i, stats_tuple in enumerate(map_data):
                infile.write(str(map_results[int(i)]) + ';')
                for item in stats_tuple:
                    infile.write(str(item) + ';')
                infile.write(str(team_name) + ';\n')
    else:   
        with open(path, 'a') as infile:
            infile.write('map_result; agent; rating; acs; kills; deaths; assists; kast; adr; hs_percent; fk; fd; team;\n')
            for i, stats_tuple in enumerate(map_data):
                infile.write(str(map_results[int(i)]) + ';')
                for item in stats_tuple:
                    infile.write(str(item) + ';')
                infile.write(str(team_name) + ';\n')

def write_team_data_to_file(team_name: str, players: list, opposing_team: str, 
                            map_name: str, map_pick: str, starting_side: 
                            str, map_result: str, scoreline: str, overtime_flag: bool,
                            match_length: str, date_of_match: str, event_name: str,
                            vod_link):
    path = f'teams\{team_name}.txt'
    if os.path.exists(path):
        with open(path, 'a') as infile:
            infile.write(str(starting_side) + ';')
            infile.write(str(map_result) + ';')
            infile.write(str(opposing_team) + ';')
            infile.write(str(map_name) + ';')
            infile.write(str(map_pick) + ';')
            for player in players:
                infile.write(str(player) + ';')
            infile.write(str(scoreline) + ';')
            infile.write(f'{overtime_flag}' + ';')
            infile.write(str(match_length) + ';')
            infile.write(str(date_of_match) + ';')
            infile.write(str(event_name) + ';')
            infile.write(str(vod_link) + ';'+ '\n')
    else:
        with open(path, 'a') as infile:
            infile.write('starting_side; map_result; opposing_team_name; map_name; map_pick; ' 
                         + 'player1; player2; player3; player4; player5; '
                         + 'scoreline; overtime;'
                         + 'match_length; date_of_match; event_name; vod_link;\n')
            infile.write(str(starting_side) + ';')
            infile.write(str(map_result) + ';')
            infile.write(str(opposing_team) + ';')
            infile.write(str(map_name) + ';')
            infile.write(str(map_pick) + ';')
            for player in players:
                infile.write(str(player) + ';')
            infile.write(str(scoreline) + ';')
            infile.write(f'{overtime_flag}' + ';')
            infile.write(str(match_length) + ';')
            infile.write(str(date_of_match) + ';')
            infile.write(str(event_name) + ';')
            infile.write(str(vod_link) + ';'+ '\n')

def invert_match_link_list(filename):
    match_link_array = np.array([])
    with open(filename, 'r') as infile:
        for line in infile:
            match_link_array = np.append(match_link_array, line)

    # Most recent match played is first
    # Reverse array such that first is the first played
    match_link_array = np.flip(match_link_array)
    
    return match_link_array

def text_file_to_array(filename):
    match_link_array = np.array([])
    with open(filename, 'r') as infile:
        for line in infile:
            match_link_array = np.append(match_link_array, line)
    
    return match_link_array