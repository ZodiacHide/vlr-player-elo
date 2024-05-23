import requests
from bs4 import BeautifulSoup
import time
import numpy as np
import os
from data_struct import *
import match_dict as md
import team_dict as td
import player_dict as pd
 
def fetch_match_data(match_url):
    '''
    Retrieves all relevant data for a chosen matchup.
    '''
    time.sleep(1)

    # Send a GET request to matches page
    response = requests.get(match_url)

    if response.status_code != 200:
        print(f"Failed to retrieve data from {match_url}. Status code: {response.status_code}")
        response.raise_for_status()
    else:
        # Parse HTML content
        parsed_content = BeautifulSoup(response.content, 'html.parser')
        
        # Div tag with class 'map' containing the stats for a given map
        map_name_element = parsed_content.find_all('div', class_='map')

        # Initialise dictionaries
        matchup = md.matchup
        A_team_dict = td.team_data
        B_team_dict = td.team_data

        for i, map_element in enumerate(map_name_element):
            current_map = matchup['maps'][i]

            # Variable to enable 
            # better data handling
            not_first_map = False
            if i > 0:
                not_first_map = True

            # Set team div tags
            A_team = map_element.find_previous_sibling('div', class_='team')
            B_team = map_element.find_next_sibling('div', class_='team mod-right')

            ## MAKE FUNC ##
            # Find and set team names
            A_team_name, A_team_starting_side = find_team_name_side(A_team)
            B_team_name, B_team_starting_side = find_team_name_side(B_team)
            A_team_dict['team_name'] = A_team_name
            B_team_dict['team_name'] = B_team_name

            # Set match team names
            matchup['teams'][0]['team_name'] = A_team_name
            matchup['teams'][1]['team_name'] = B_team_name

            # Set team scores
            A_team_t_score, A_team_ct_score, A_team_ot_score = get_team_ct_t_score(A_team)
            B_team_t_score, B_team_ct_score, B_team_ot_score = get_team_ct_t_score(B_team)
            current_map['scoreline']['overtime']['team_a'] = A_team_ot_score
            current_map['scoreline']['overtime']['team_b'] = B_team_ot_score

            ## MAKE FUNC ##
            if A_team_starting_side == 't':
                current_map['starting_sides']['team_a'] = 'Attack'
                current_map['starting_sides']['team_b'] = 'Defense'

                current_map['scoreline']['first_half']['team_a'] = A_team_t_score
                current_map['scoreline']['second_half']['team_a'] = A_team_ct_score

                current_map['scoreline']['first_half']['team_b'] = B_team_ct_score
                current_map['scoreline']['second_half']['team_b'] = B_team_t_score
            else:
                current_map['starting_sides']['team_b'] = 'Attack'
                current_map['starting_sides']['team_a'] = 'Defense'

                current_map['scoreline']['first_half']['team_a'] = A_team_ct_score
                current_map['scoreline']['second_half']['team_a'] = A_team_t_score

                current_map['scoreline']['first_half']['team_b'] = B_team_t_score
                current_map['scoreline']['second_half']['team_b'] = B_team_ct_score  

            # Remove empty spaces from map name header and join with ','
            joined_map_element = ','.join(map_element.get_text().split())
            split_map_element = joined_map_element.split(',')

            # Set mape name and map length
            # 2nd element is just 'PICK'
            map_name = split_map_element[0]
            map_time_length = split_map_element[-1]

            # Find team who picked map
            map_picker = map_element.find('span', class_='picked mod-1 ge-text-light')
            if map_picker:
                # mod-1 is A
                current_map['picked_by'] = A_team_name
            else:
                # mod-2 is B
                current_map['picked_by'] = B_team_name

            current_map['map_name'] = map_name
            current_map['map_length'] = map_time_length

            # Getting Player Data #
            parent_element = map_element.find_parent('div').find_parent('div')

            ## MAKE FUNC ##
            ## A Team
            left_team_player_element_whole = parent_element.find_next('table', class_='wf-table-inset mod-overview')
            left_team_player_elements = left_team_player_element_whole.find('tbody')
            A_players = left_team_player_elements.find_all('tr')

            ## B Team
            right_team_player_element_whole = left_team_player_element_whole.find_next('table', class_='wf-table-inset mod-overview')
            right_team_player_elements = right_team_player_element_whole.find('tbody')
            B_players = right_team_player_elements.find_all('tr')

            # Change values of player for current map
            for k, player_set in enumerate((A_players, B_players)):
                for n, element in enumerate(player_set):
                    current_player = matchup['teams'][k]['players'][n]['matches'][i]
                    
                    ## Player Name
                    player_name_string = element.find('div', class_='text-of').string
                    player_name = ''.join(player_name_string.split())

                    # Not given players are always in same order, check for order
                    # and correct current_player variable
                    if not_first_map and player_name == matchup['teams'][k]['players'][n]['player_name']:
                        pass
                    elif not_first_map:
                        for l, player in enumerate(matchup['teams'][k]['players']):
                            if player['player_name'] == player_name:
                                current_player = matchup['teams'][k]['players'][l]['matches'][i]
                    else: 
                        matchup['teams'][k]['players'][n]['player_name'] = player_name

                    ## Player Agent
                    player_agent_element = element.find('img')
                    player_agent_name = player_agent_element['title']
                    current_player['agent'] = player_agent_name
                    
                    sub_elements = element.find_all('td')
                    for j, item in enumerate(sub_elements):
                        # j = 0 - player name
                        # j = 1 - agent name
                        # 2 - 13 {Rating, ACS, K, D, A, 
                        #        KD Diff, KAST, ADR, HS, 
                        #        FK, FD, FK Diff}
                                                
                        if j < 2:
                            continue
                        if j == 5:
                            # Adress 'Death' edge case span design
                            item_span = item.find('span').find_next('span').find_next('span')
                            item_total = item_span.find_next('span').string
                        else:
                            item_span = item.find('span')
                            item_total = item_span.find_next('span').string

                        # Adress 'XX%' case and remove % to allow for float array
                        # ignore 7th index, KD Diff not saved
                        stat_names = ['rating', 'acs', 'kills', 'deaths', 
                                        'assists', '', 'kast', 'adr', 
                                        'hs_percent', 'fk', 'fd']
                        if j != 7 and j < 13:
                            try:
                                current_player[stat_names[j-2]] = item_total
                            except ValueError:
                                current_player[stat_names[j-2]] = item_total[:-1]

        # Event name #
        match_header_element = parsed_content.find('div', class_="match-header-super")
        event_element = match_header_element.find_next('div')
        event_name_raw = event_element.find('div', class_='match-header-event-series').find_previous('div').string
        event_name = ' '.join(event_name_raw.split())
        matchup['event_name'] = event_name

        # Time of match #
        match_date_element = match_header_element.find('div', class_='match-header-date')
        match_date_date_div = match_date_element.find_next('div')
        match_date_date = ' '.join(match_date_date_div.string.split())
        match_date_time_div = match_date_date_div.find_next('div')
        match_date_time = ' '.join(match_date_time_div.string.split())
        time_of_matchup = ', '.join([match_date_date, match_date_time])
        matchup['matchup_start_time'] = time_of_matchup

        # Scoreline #
        scoreline_element = parsed_content.find('div', class_='match-header-vs-score')
        scoreline_div = scoreline_element.find('div', class_='js-spoiler')
        scoreline_team_1 = scoreline_div.find_next('span')
        scoreline_team_1_str = ''.join(scoreline_team_1.string.split())
        scoreline_team_2 = scoreline_team_1.find_next('span').find_next('span')
        scoreline_team_2_str = ''.join(scoreline_team_2.string.split())
        scoreline = ':'.join([scoreline_team_1_str, scoreline_team_2_str])
        matchup['final_scoreline'] = scoreline 

        # Format #
        # 2 match-header-vs-notes, last one is format.
        format_div = scoreline_element.find_all_next('div', class_='match-header-vs-note')[-1]
        format = ''.join(format_div.string.split())
        matchup['format'] = format

        # VODs #
        vods_element = parsed_content.find_all('div', class_='match-streams-container')[-1]
        vods_links = vods_element.find_all('a')
        vods_links = [link.get('href') for link in vods_links]
        vods_links = np.array(vods_links)
    
        for i in range(len(vods_links)):
            matchup['maps'][i]['vod_link'] = vods_links[i]

        return matchup

match_url = invert_match_link_list('test_urls.txt')
for url in match_url:
    # Initialise values #
    # Data from match played
    matchup_data = fetch_match_data(match_url=url)

    # Strings containing team names
    team_a_name = matchup_data['teams'][0]['team_name']
    team_b_name = matchup_data['teams'][1]['team_name']
    
    # String containing final scoreline
    scoreline = matchup_data['final_scoreline']
    integer_scoreline = int(scoreline[0])+int(scoreline[-1])

    # List containing dicts of all maps played
    maps = matchup_data['maps']

    ## Write data to files ##
    for team in matchup_data['teams']:
        # List to store player names
        player_names = []
        team_name = team['team_name']
        for player in team['players']:
            # Add player name to list
            player_names.append(player['player_name'])

            # Write player data to file
            write_player_data_to_file(player_data=player, team_name=team_name, maps=maps,
                                      scoreline=scoreline, team_a_name=team_a_name,
                                      team_b_name=team_b_name)

        for i, map in enumerate(maps):
            # Flag to know which scoreline is team's
            team_is_a = False

            # Flag to check for overtime
            overtime_flag = False

            # Set map name and picked by
            map_name = map['map_name']
            # If last map, it's a decider
            if i+1 == integer_scoreline:
                map_pick = 'Decider'
            else:
                map_pick = map['picked_by']

            # Verify which team is which
            if team_name == team_a_name:
                opposing_team = team_b_name
                team_is_a = True
            else:
                opposing_team = team_a_name

            # Check to avoid errors
            if i+1 > integer_scoreline:
                continue

            # Check for overtime
            if map['scoreline']['overtime']['team_a'] > 0 or map['scoreline']['overtime']['team_b'] > 0:
                overtime_flag = True

            # Evaluate the result of the map
            if team_is_a:
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
            
            write_team_data_to_file(team_name=team_name, players=player_names, 
                                    opposing_team=opposing_team, map_name=map_name, map_pick=map_pick,
                                    starting_side=starting_side, map_result=map_result, 
                                    scoreline=f'{team_score}:{opposing_score}', overtime_flag=overtime_flag)
