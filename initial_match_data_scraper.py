import requests
from bs4 import BeautifulSoup
import time
import numpy as np
import os
import data_struct as struct
from data_struct import player_dtype, team_data_dtype, map_dtype, find_team_name_side, get_team_ct_t_score
import match_dict as md
import team_dict as td
import player_dict as pd
 
def invert_match_link_list():
    match_link_array = np.array([])
    with open('test_urls.txt', 'r') as infile:
        for line in infile:
            match_link_array = np.append(match_link_array, line)

    # with open('C:\\Users\\Simen\\Desktop\\valorant-rankings\\match_urls.txt', 'r') as infile:
    #     for line in infile:
    #         match_link_array = np.append(match_link_array, line)

    # Reverse array
    # First match played is first in list
    match_link_array = np.flip(match_link_array)
    
    return match_link_array

def fetch_match_data(match_link_array):
    '''
    Retrieves all relevant data in a match:
    Per Matchup:
    Event name, Time of match,
    Team names, Player names, Format, Scoreline.

    Data per map: 
    Winner, Loser, Map name, team pick, Starting side, 
    {Team name, first half, second half}

    Per team:

    Per player:
    Player name, Agent, Rating, ACS, Kills, Deaths, Assist, 
    KAST, ADR, HS%, FK, FD
    
    Stored in numpy.ndarray{[match1][match2]}
    match1 = np.ndarray{[Event name, Time of match, Team names, player names, format, scoreline], [VODs], [map1],[map2],...}
    map1 = np.ndarray{[Winner, Loser, Map name, team pick, map length, winner score, loser score], [team1], [team2]}
    team1 = np.ndarray{[Team name, starting side, rounds won first half, rounds won second half], [player1], [player2],...}
    player1 = np.ndarray{[Player name, Agent, Rating, ACS, Kills, Deaths, Assists, KAST, ADR, HS%, FK, FD]}'''

    matches_data = np.zeros(0)
    for match_url in match_link_array:
        time.sleep(1)

        # Send a GET request to matches page
        response = requests.get(match_url)

        if response.status_code == 200:
            # Parse HTML content
            parsed_content = BeautifulSoup(response.content, 'html.parser')

            # Get map names and map lengths
            map_name_element = parsed_content.find_all('div', class_='map')

            # Empty array for amount of matches
            map_num = 0

            matchup = md.matchup
            A_team_dict = td.team_data
            B_team_dict = td.team_data

            for i, map_element in enumerate(map_name_element):
                current_map = matchup['maps'][i]
                not_first_map = False
                # If on second map, skip redundant
                if i > 0:
                    not_first_map = True

                # Set team elements
                A_team = map_element.find_previous_sibling('div', class_='team')
                B_team = map_element.find_next_sibling('div', class_='team mod-right')

                # Find the map winner
                A_team_name, A_team_starting_side, team_A_won = find_team_name_side(A_team)
                
                ## MAKE FUNC ##
                # A is winner
                if 'mod-win' in team_A_won.get('class', []):
                    A_team_t_score, A_team_ct_score = get_team_ct_t_score(A_team)
                # A is not winner
                else:
                    A_team_t_score, A_team_ct_score = get_team_ct_t_score(A_team)

                # A team basic info
                A_team_dict['team_name'] = A_team_name
                
                # fubar is never used
                # B team basic info
                B_team_name, B_team_starting_side, fubar = find_team_name_side(B_team)
                B_team_t_score, B_team_ct_score = get_team_ct_t_score(B_team)

                B_team_dict['team_name'] = B_team_name

                # map i basic info
                matchup['teams'][0]['team_name'] = A_team_name
                current_map['starting_sides']['team_a'] = A_team_starting_side

                matchup['teams'][1]['team_name'] = B_team_name
                current_map['starting_sides']['team_b'] = B_team_starting_side

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

                # Remove empty spaces and join with ,
                joined_map_element = ','.join(map_element.get_text().split())
                split_map_element = joined_map_element.split(',')

                # Find team who picked map
                map_picker = map_element.find('span', class_='picked mod-1 ge-text-light')
                if map_picker:
                    # mod-1 is A
                    current_map['picked_by'] = A_team_name
                else:
                    # mod-2 is B
                    current_map['picked_by'] = B_team_name

                # 2nd element is just 'PICK'
                map_name = split_map_element[0]
                map_time_length = split_map_element[-1]

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
                                    # print("j = ", j)
                                    # print(stat_names[j-2], item_total)
                                    current_player[stat_names[j-2]] = item_total
                                except ValueError:
                                    # print("j = ", j)
                                    # print(stat_names[j-2], item_total[:-1])
                                    current_player[stat_names[j-2]] = item_total[:-1]
                map_num += 1

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
        else:
            print(f"Failed to retrieve data from {match_url}. Status code: {response.status_code}")
            continue

match_link_array = invert_match_link_list()
matchup_data = fetch_match_data(match_link_array=match_link_array)

print(matchup_data['event_name'],
       matchup_data['matchup_start_time'],
       matchup_data['format'],
       matchup_data['final_scoreline'])

team_a = matchup_data['teams'][1]
for player in team_a['players']:
    if player['player_name'] == 'babykiwii':
        sawamura = player
        break 

print(sawamura['matches'][0].items())

def write_player_data_to_file(player_data, teamname, result, filename, agent):
    if os.path.exists(f'players\{filename}'):
        with open(f'players\{filename}', 'a') as infile:
            infile.write('\n' + agent + '; ')
            for item in player_data:
                if isinstance(item, np.ndarray):
                    infile.write(str(item[0]) + '; ')
    else:
        with open(f'players\{filename}', 'a') as infile:
            infile.write('agent; rating; acs; kills; deaths; assists; kast; adr; hsp; fk; fd; team; elo; elo_change;\n')
            infile.write(agent + '; ')
            for item in player_data:
                if isinstance(item, np.ndarray):
                    infile.write(str(item[0]) + '; ')
                    # Write if map won or lost
                    # if teamname != map_data[0][0]:
                        # ...
                    # if player_data
                    # Write new Elo
                    # Write elo gain/loss

### Make file / Append stats to file for every player in match - New players get fresh elo as stat in file ###
### Then compare team1 elo to team2 elo ###
### Do elo calculations ###
### Update elo in file ###