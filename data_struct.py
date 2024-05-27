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
            ct_score = int(final_score.get_text())
            t_score = 0
        else:
            final_score = team.find('div', style='margin-left: 8px;')
            ct_score = int(final_score.get_text())
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
    player_name = remove_illegal_chars_in_filename(player_name)
    map_count = int(scoreline[0]) + int(scoreline[-1])
    path = f'players\\{player_name}.txt'
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
        with open(path, 'a', encoding="utf-8") as infile:
            for i, stats_tuple in enumerate(map_data):
                infile.write(str(map_results[int(i)]) + ';')
                for item in stats_tuple:
                    infile.write(str(item) + ';')
                infile.write(str(team_name) + ';\n')
    else:   
        with open(path, 'a', encoding="utf-8") as infile:
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
                            vod_link) -> None:
    # Check if string contains illegal characters
    # Remove if found
    team_name = remove_illegal_chars_in_filename(team_name)

    path = f'teams\\{team_name}.txt'
    if os.path.exists(path):
        with open(path, 'a', encoding="utf-8") as infile:
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
        with open(path, 'a', encoding="utf-8") as infile:
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

def invert_match_link_list(filename) -> np.ndarray:
    match_link_array = np.array([])
    with open(filename, 'r') as infile:
        for line in infile:
            match_link_array = np.append(match_link_array, line)

    # Most recent match played is first
    # Reverse array such that first is the first played
    match_link_array = np.flip(match_link_array)
    
    return match_link_array

def text_file_to_array(filename) -> np.ndarray:
    match_link_array = np.array([])
    with open(filename, 'r') as infile:
        for line in infile:
            match_link_array = np.append(match_link_array, line)
    
    return match_link_array

def choose_match_format(scoreline: str) -> str:
    team_scores = [int(scoreline[0]), int(scoreline[-1])]
    scoreline_sum = np.sum(team_scores)
    match_format = 'bo0'
    if scoreline_sum >= 13:
        # Assume bo1 (13-x)
        match_format = 'bo1'
    elif scoreline_sum == 1:
        # Assume bo1 (1-0)
        match_format = 'bo1'
    elif scoreline_sum == 2:
        # Assume bo2 (1-1)
        match_format = 'bo2'
        # If either team has 0 points, it's bo3 (2-0)
        if team_scores[0] == 0 or team_scores[1] == 0:
            match_format = 'bo3'
    elif scoreline_sum == 3:
        # Assume bo3 (2-1)
        match_format == 'bo3'
        # If either team has 0 points, it's bo5 (3-0)
        if team_scores[0] == 0 or team_scores[1] == 0:
            match_format = 'bo5'
    elif scoreline_sum == 4:
        # Assume bo5 (3-1)
        match_format = 'bo5'
    elif scoreline_sum == 5:
        # Assume bo5 (3-2)
        match_format = 'bo5'
        # If either team has 0 points, it's bo7 (5-0)
        if team_scores[0] == 0 or team_scores[1] == 0:
            match_format = 'bo7'
    elif scoreline_sum > 5 and scoreline_sum <= 9:
        # assume bo7 (5-1), (5-2), (5-3), (5-4)
        match_format = 'bo7'
    
    return match_format

def evaluate_map_result(map: dict, flag: bool) -> tuple:
    if flag:
        team_first_half = map['scoreline']['first_half']['team_a']
        team_second_half = map['scoreline']['second_half']['team_a']
        team_ot = map['scoreline']['overtime']['team_a']
        team_score = team_first_half + team_second_half + team_ot
        
        opposing_first_half = map['scoreline']['first_half']['team_b']
        opposing_second_half = map['scoreline']['second_half']['team_b']
        opposing_ot = map['scoreline']['overtime']['team_b']
        opposing_score = opposing_first_half + opposing_second_half + opposing_ot

        starting_side = map['starting_sides']['team_a']
        if team_score > opposing_score:
            map_result = 'W'
        else:
            map_result = 'L'
    else:
        team_first_half = map['scoreline']['first_half']['team_b']
        team_second_half = map['scoreline']['second_half']['team_b']
        team_ot = map['scoreline']['overtime']['team_b']
        team_score = team_first_half + team_second_half + team_ot
        
        opposing_first_half = map['scoreline']['first_half']['team_a']
        opposing_second_half = map['scoreline']['second_half']['team_a']
        opposing_ot = map['scoreline']['overtime']['team_a']
        opposing_score = opposing_first_half + opposing_second_half + opposing_ot

        starting_side = map['starting_sides']['team_b']
        if team_score > opposing_score:
            map_result = 'W'
        else:
            map_result = 'L'

    return map_result, starting_side, team_score, opposing_score

def get_event_name_date_scoreline(parsed_content: bs4.element.Tag) -> tuple:
    # Event name #
    try:
        match_header_element = parsed_content.find('div', class_="match-header-super")
        event_element = match_header_element.find_next('div')
        event_name_raw = event_element.find('div', class_='match-header-event-series').find_previous('div').string
        event_name = ' '.join(event_name_raw.split())
    except:
        event_name = 'None'
        
    # Time of match #
    match_date_element = match_header_element.find('div', class_='match-header-date')
    match_date_date_div = match_date_element.find_next('div')
    try:
        match_date_date = ' '.join(match_date_date_div.string.split())
    except:
        match_date_date = 'None'
    try:
        match_date_time_div = match_date_date_div.find_next('div')
        match_date_time = ' '.join(match_date_time_div.string.split())
    except:
        match_date_time = 'None'
    time_of_matchup = ', '.join([match_date_date, match_date_time])

    # Scoreline #
    try:
        scoreline_element = parsed_content.find('div', class_='match-header-vs-score')
        scoreline_div = scoreline_element.find('div', class_='js-spoiler')
        scoreline_team_1 = scoreline_div.find_next('span')
        scoreline_team_1_str = ''.join(scoreline_team_1.string.split())
        scoreline_team_2 = scoreline_team_1.find_next('span').find_next('span')
        scoreline_team_2_str = ''.join(scoreline_team_2.string.split())
        scoreline = ':'.join([scoreline_team_1_str, scoreline_team_2_str])
    except:
        scoreline = '0:0'

    return event_name, time_of_matchup, scoreline

def get_essential_if_not_played(parsed_content: bs4.element.Tag) -> tuple:
    event_name, time_of_matchup, scoreline = get_event_name_date_scoreline(parsed_content=parsed_content)
    
    # Find large left team name #
    A_team_name = parsed_content.find('div', class_='match-header-link-name mod-1').get_text()
    A_team_name = ''.join(A_team_name.split())

    # Find large right team name #
    B_team_name = parsed_content.find('div', class_='match-header-link-name mod-2').get_text()
    B_team_name = ''.join(B_team_name.split())
    return time_of_matchup, event_name, A_team_name, B_team_name, scoreline

def get_user_input_on_scraping():
    user_input = input('Continue with scraping? Yes: y, No: n \n')
    if user_input == 'Y' or user_input == 'y':
        try:
            no_scrape = input('How many urls? Input integer: ')
            no_matchups_to_do = int(no_scrape)
            return no_matchups_to_do
        except ValueError:
            # Poor input, try again
            print("Poor user input, try again.\n")
            return get_user_input_on_scraping()
    elif user_input == 'N' or user_input == 'n':
        return None
    else:
        # Poor input, try again
        print("Poor user input, try again.\n")
        return get_user_input_on_scraping()

def remove_illegal_chars_in_filename(str_string: str):
    # Check if string contains illegal characters
    # Remove if found
    illegal_file_chars = ['<','>',':','"','/',"\\",'|','?','*']
    for char in illegal_file_chars:
        if char in str_string:
            str_string = ''.join([string.replace(char,'') for string in str_string])
    
    return str_string

