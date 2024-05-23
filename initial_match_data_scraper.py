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
            maps_arr = np.zeros(len(map_name_element), dtype=map_dtype)
            A_team_dict = td.team_data
            B_team_dict = td.team_data
            team_data = np.zeros((len(map_name_element), 1), dtype=team_data_dtype)
            A_team_players = np.zeros((len(map_name_element), 5, 1), dtype=player_dtype)
            B_team_players = np.zeros((len(map_name_element), 5, 1), dtype=player_dtype)
            for i, map_element in enumerate(map_name_element):
                current_map = matchup['maps'][i]

                # Set default
                B_won_map = True

                # Set team elements
                A_team = map_element.find_previous_sibling('div', class_='team')
                B_team = map_element.find_next_sibling('div', class_='team mod-right')

                # Find the map winner
                A_team_name, A_team_starting_side, team_A_won = find_team_name_side(A_team)
                
                ## MAKE FUNC ##
                # A is winner
                if 'mod-win' in team_A_won.get('class', []):
                    A_team_t_score, A_team_ct_score = get_team_ct_t_score(A_team)
                    A_team_score = A_team_t_score + A_team_ct_score
                    B_won_map = False
                # A is not winner
                else:
                    A_team_t_score, A_team_ct_score = get_team_ct_t_score(A_team)
                    A_team_score = A_team_t_score + A_team_ct_score
                    B_won_map = True

                # A team basic info
                A_team_dict['team_name'] = A_team_name
                
                # fubar is never used
                # B team basic info
                B_team_name, B_team_starting_side, fubar = find_team_name_side(B_team)
                B_team_t_score, B_team_ct_score = get_team_ct_t_score(B_team)
                B_team_score = B_team_t_score + B_team_ct_score

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
                    team_pick = A_team_name
                    current_map['picked_by'] = A_team_name
                else:
                    # mod-2 is B
                    team_pick = B_team_name
                    current_map['picked_by'] = B_team_name

                # 2nd element is just 'PICK'
                map_name = split_map_element[0]
                map_time_length = split_map_element[-1]

                current_map['map_name'] = map_name
                current_map['map_length'] = map_time_length

                ## MAKE FUNC ##
                # Delete #
                if B_won_map:
                    map_winner = B_team_name
                    map_winner_score = B_team_score
                    map_loser = A_team_name
                    map_loser_score = A_team_score
                else:
                    map_winner = A_team_name
                    map_winner_score = A_team_score
                    map_loser = B_team_name
                    map_loser_score = B_team_score

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


                for k, player_set in enumerate((A_players, B_players)):
                    for n, element in enumerate(player_set):
                        current_player = matchup['teams'][k]['players'][n]['matches'][i]
                        if k != 0:
                            player_team_name = B_team_name
                        else:
                            player_team_name = A_team_name

                        ## Player Name
                        player_name_string = element.find('div', class_='text-of').string
                        player_name = ''.join(player_name_string.split())
                        matchup['teams'][k]['players'][n]['player_name'] = player_name

                        ## Player Agent
                        player_agent_element = element.find('img')
                        player_agent_name = player_agent_element['title']
                        current_player['agent'] = player_agent_name
                        
                        sub_elements = element.find_all('td')
                        player_game_stats = np.zeros((len(sub_elements)-2, 3), dtype=float)
                        for j, item in enumerate(sub_elements):
                            # j = 0 - player name
                            # j = 1 - agent name
                            # 2 - 13 {Rating, ACS, K, D, A, 
                            #        KD Diff, KAST, ADR, HS, 
                            #        FK, FD, FK Diff}
                            
                            # ignore 7th index, KD Diff not saved
                            stat_names = ['rating', 'acs', 'kills', 'deaths', 'assists', 'kast', 'adr', 'hs_percent', 'fk', 'fd']
                            
                            ###
                            # Remove ct and t elements after revision, not saved
                            ###
                            if j < 2:
                                continue
                            if j == 5:
                                # Adress 'Death' edge case span design
                                item_span = item.find('span').find_next('span').find_next('span')
                                item_total = item_span.find_next('span').string
                                item_t = item_total.find_next('span').string
                                item_ct = item_t.find_next('span').string
                            else:
                                item_span = item.find('span')
                                item_total = item_span.find_next('span').string
                                item_t = item_total.find_next('span').string
                                item_ct = item_t.find_next('span').string

                            # Adress 'XX%' case and remove % to allow for float array
                            try:
                                player_game_stats[j-2][0] = item_total
                                player_game_stats[j-2][1] = item_t
                                player_game_stats[j-2][2] = item_ct
                            except ValueError:
                                player_game_stats[j-2][0] = item_total[:-1]
                                player_game_stats[j-2][1] = item_t[:-1]
                                player_game_stats[j-2][2] = item_ct[:-1]
                            
                            if j != 7 and j < 12:
                                try:
                                    current_player[stat_names[j-2]] = item_total
                                except ValueError:
                                    current_player[stat_names[j-2]] = item_total[:-1]


                        player_data = player_name, player_agent_name, player_team_name, player_game_stats
                        if k != 0:
                            B_team_players[i][n] = player_data
                        else:
                            A_team_players[i][n] = player_data

                ## MAKE FUNC ##
                # team1 = np.ndarray{[Team name, starting side, rounds won first half, rounds won second half], [player1], [player2],...}
                if A_team_starting_side == 't':
                    left_team_data = (A_team_name, A_team_starting_side, A_team_t_score, A_team_ct_score)
                    right_team_data = (B_team_name, A_team_starting_side, B_team_ct_score, B_team_t_score)
                else:
                    left_team_data = (A_team_name, A_team_starting_side, A_team_ct_score, A_team_t_score)
                    right_team_data = (B_team_name, A_team_starting_side, B_team_t_score, B_team_ct_score)

                # left_team_data = np.array(inter_left_team_data, dtype=team_dtype)
                # right_team_data = np.array(inter_right_team_data, dtype=team_dtype)
                
                # Collect all team data in one array #
                team_data[map_num] = (left_team_data, right_team_data)
                # team_data = np.array(inter_team_data, dtype=inter_team_dtype)

                # Map data #
                map_data = (map_winner, map_loser, map_name, team_pick, map_time_length, map_winner_score, map_loser_score)
                # map_data = np.array(inter_map_data, dtype=map_dtype)

                # Put map data in array for all maps #
                maps_arr[map_num] = map_data
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

            # Team names #
            team_name_1_element = parsed_content.find('div', class_='wf-title-med')
            team_name_1 = ' '.join(team_name_1_element.string.split())

            team_name_2_element = parsed_content.find('div', class_='wf-title-med mod-single')
            team_name_2 = ' '.join(team_name_2_element.string.split())

            # Scoreline #
            scoreline_element = parsed_content.find('div', class_='match-header-vs-score')
            scoreline_div = scoreline_element.find('div', class_='js-spoiler')
            scoreline_team_1 = scoreline_div.find_next('span')
            scoreline_team_1_str = ''.join(scoreline_team_1.string.split())
            scoreline_team_2 = scoreline_team_1.find_next('span').find_next('span')
            scoreline_team_2_str = ''.join(scoreline_team_2.string.split())

            scoreline = ':'.join([scoreline_team_1_str, scoreline_team_2_str])

            # Format #
            # 2 match-header-vs-notes, last one is format.
            format_div = scoreline_element.find_all_next('div', class_='match-header-vs-note')[-1]
            format = ''.join(format_div.string.split())


            # VODs #
            vods_element = parsed_content.find_all('div', class_='match-streams-container')[-1]
            vods_links = vods_element.find_all('a')
            vods_links = [link.get('href') for link in vods_links]
            vods_links = np.array(vods_links)

            match_data = [event_name, time_of_matchup, team_name_1, team_name_2, scoreline, format, map_num, vods_links.tolist()]
            return match_data, maps_arr, team_data, A_team_players, B_team_players 
        else:
            print(f"Failed to retrieve data from {match_url}. Status code: {response.status_code}")
            continue

match_link_array = invert_match_link_list()
match_data, maps_arr, team_data, A_players, right_player = fetch_match_data(match_link_array=match_link_array)

# Sample data in classes #
def _create_player_stats(username, agent, rating, acs, kills, deaths, assists, kast, adr, hsp, fk, fd):
    return struct.playerStats(username, agent, rating, acs, kills, deaths, assists, kast, adr, hsp, fk, fd)

def _create_team_stats(name, startside, first_half, second_half, player_data):
    return struct.teamStats(name, startside, first_half, second_half, [_create_player_stats(
        player_data[i][0][0], player_data[i][0][1], player_data[i][0][3][0], player_data[i][0][3][1], 
        player_data[i][0][3][2], player_data[i][0][3][3], player_data[i][0][3][4], player_data[i][0][3][5], 
        player_data[i][0][3][6], player_data[i][0][3][7], player_data[i][0][3][8], player_data[i][0][3][9]) for i in range(5)])

def _create_map_data(winner, loser, map_name, picked_by, map_time_length, winner_score, loser_score, 
                     A_players, B_players,
                     name, startside, first_half, second_half) -> list:
    return struct.mapData(winner, loser, map_name, picked_by, map_time_length, winner_score, loser_score, 
                          [_create_team_stats(name[0][0][0], startside[0][0][1], first_half[0][0][2], second_half[0][0][3], A_players),
                           _create_team_stats(name[0][1][0], startside[0][1][1], first_half[0][1][2], second_half[0][1][3], B_players)])

def create_series_data(match_data, maps_arr, team_data, A_players, B_players):
    # gameSeries dependencies
    event_name=match_data[0]
    time_of_series=match_data[1] 
    teams=[match_data[2], match_data[3]]
    scoreline=match_data[4] 
    format=match_data[5] 
    num_maps=match_data[6] 
    vods=match_data[7]

    # mapData dependencies
    winner=[maps_arr[0][0], maps_arr[1][0]]
    loser=[maps_arr[0][1], maps_arr[1][1]]
    map_name=[maps_arr[0][2], maps_arr[1][2]]
    picked_by=[maps_arr[0][3], maps_arr[1][3]]
    map_time_length=[maps_arr[0][4], maps_arr[1][4]]
    winner_score=[maps_arr[0][5], maps_arr[1][5]]
    loser_score=[maps_arr[0][6], maps_arr[1][6]]

    # _create_map_data dependencies
    name=[team_data[0], team_data[1]]
    startside=[team_data[0], team_data[1]]
    first_half=[team_data[0], team_data[1]] 
    second_half=[team_data[0], team_data[1]]

    return struct.gameSeries(event_name, time_of_series, teams, scoreline, format, num_maps, vods, 
                             [_create_map_data(winner[i], loser[i], map_name[i], picked_by[i], map_time_length[i], 
                                               winner_score[i], loser_score[i], A_players[i], B_players[i], 
                                               name[i], startside[i], first_half[i], second_half[i]) for i in range(num_maps)])

series = create_series_data(match_data, maps_arr, team_data, A_players, right_player)
final_data = []
for attribute, value in series.__dict__.items():
    final_data.append(value)

thing = final_data[-1]
match_info = final_data[:-1]

map = [[],[]]
for i in range(len(thing)):
    for attribute, value in thing[i].__dict__.items():
        map[i].append(value)

# print(map)
team = [[[],[]],[[],[]]]
for i in range(len(map)):
    for j in range(len(map[0][-1])):
        for attribute, value in map[i][-1][j].__dict__.items():
            team[i][j].append(value)

players = np.empty((len(map),2,5,12)).tolist()
for i in range(len(team)):
    for j in range(2):
        for k in range(5):
            for l, (attribute, value) in enumerate(team[i][j][-1][k].__dict__.items()):
                players[i][j][k][l] = value

print(team[0][0])
print(team[0][1])
# print(players[0][0][0])

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

# result = np.zeros((len(map), 3), dtype=np.dtype('U50'))
# for i in range(len(map)):
#     # if first score is higher than second, first team won
#     left_score = map[i][5]
#     right_score = map[i][6]
#     if left_score > right_score:
#         result[i][0] = map[i][0] # teamname
#         result[i][1] = left_score
#         result[i][2] = right_score
#     else:
#         result[i][0] = map[i][1] 
#         result[i][1] = right_score
#         result[i][2] = left_score

#     for j in range(5):
#         write_player_data_to_file(players[i][0][0], result, f'{players[0][0][0][0]}.txt', f'{players[0][0][0][1]}')


### Make file / Append stats to file for every player in match - New players get fresh elo as stat in file ###
### Then compare team1 elo to team2 elo ###
### Do elo calculations ###
### Update elo in file ###