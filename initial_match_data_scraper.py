import requests
from bs4 import BeautifulSoup
import time
import numpy as np
import os
import copy
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
        matchup = copy.deepcopy(md.matchup)
        A_team_dict = copy.deepcopy(td.team_data)
        B_team_dict = copy.deepcopy(td.team_data)

        if not map_name_element:
            (time_of_matchup, event_name, 
             A_team_name, B_team_name, scoreline
             ) = get_essential_if_not_played(parsed_content=parsed_content)

            matchup['event_name'] = event_name
            matchup['matchup_start_time'] = time_of_matchup
            matchup['final_scoreline'] = scoreline
            return matchup, time_of_matchup, event_name, A_team_name, B_team_name, scoreline

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
                        # Check if player exists and which position 
                        # current player is in set that position to active current player
                        player_found = False
                        for l, player in enumerate(matchup['teams'][k]['players']):
                            if player['player_name'] == player_name:
                                current_player = matchup['teams'][k]['players'][l]['matches'][i]
                                player_found = True
                                break
                        if not player_found:
                            # Player was not in previous match
                            # Make new dict, set player name
                            player_dict = copy.deepcopy(matchup['teams'][k]['players'][n])
                            player_dict['player_name'] = player_name

                            keys = list(player_dict['matches'][0].keys())
                            # Set values for previous matches
                            for m in range(i):
                                for key in keys:
                                    player_dict['matches'][m][key] = 0
                                player_dict['matches'][m]['agent'] = "None"

                            # Append new dict to existing team
                            matchup['teams'][k]['players'].append(player_dict)
                            current_player = matchup['teams'][k]['players'][-1]['matches'][i]
                    elif not not_first_map:
                        # For first map, set player names 
                        matchup['teams'][k]['players'][n]['player_name'] = player_name

                    ## Player Agent
                    try:
                        player_agent_element = element.find('img')
                        player_agent_name = player_agent_element['title']
                        current_player['agent'] = player_agent_name
                    except:
                        # Handle abnormal datapoints
                        continue
                    
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

        event_name, time_of_matchup, scoreline = get_event_name_date_scoreline(parsed_content=parsed_content)
        matchup['event_name'] = event_name
        matchup['matchup_start_time'] = time_of_matchup
        matchup['final_scoreline'] = scoreline

        # Format #
        # Utilise scoreline to find format
        matchup['format'] = choose_match_format(scoreline=scoreline)

        # VODs #
        vods_element = parsed_content.find_all('div', class_='match-streams-container')[-1]
        vods_links = vods_element.find_all('a')
        vods_links = [link.get('href') for link in vods_links]
        vods_links = np.array(vods_links)

        if len(vods_links) == 1:
            for i in range(len(map_element)):
                matchup['maps'][i]['vod_link'] = vods_links[0]
        else:
            try:
                for i in range(len(vods_links)):
                    matchup['maps'][i]['vod_link'] = vods_links[i]
            except IndexError:
                for i in range(1, len(vods_links)):
                    matchup['maps'][i-1]['vod_link'] = vods_links[i-1]

        return matchup, time_of_matchup, event_name, A_team_name, B_team_name, scoreline

def main():
    match_urls = text_file_to_array('match_urls_by_date.txt')
    no_matchups_to_do = 0
    for matchup_count, url in enumerate(match_urls):
        if matchup_count < 7000:
            continue
        if matchup_count - no_matchups_to_do >= 0:
            new_no = get_user_input_on_scraping()
            if new_no == None:
                break
            no_matchups_to_do += new_no
            
        # Initialise values #
        # Data from match played
        (matchup_data, date_of_match, event_name, 
         team_a_name, team_b_name, scoreline) = fetch_match_data(match_url=url)
        
        # Integer value containing sum of final scoreline
        integer_scoreline = int(scoreline[0])+int(scoreline[-1])

        # List containing dicts of all maps played
        maps = matchup_data['maps']

        ## Write data to files ##
        for team_count, team in enumerate(matchup_data['teams']):
            # List to store player names
            player_names = []
            team_name = team['team_name']
            for player in team['players']:
                # Add player name to list
                player_names.append(player['player_name'])

                # Write player data to file
                try:
                    write_player_data_to_file(player_data=player, team_name=team_name, maps=maps,
                                            scoreline=scoreline, team_a_name=team_a_name,
                                            team_b_name=team_b_name)
                except:
                    infile.write(f"Failed to write player on line: {matchup_count+1}, Player: {player['player_name']}, Team: {team_name}\n")
                    with open('error.txt', 'a') as infile:
                        infile.write(f"Failed to write player on line: {matchup_count+1}, Player: {player['player_name']}, Team: {team_name}\n")

            # If the matchup wasn't played #
            if integer_scoreline == 0:
                # Fill in empty team names
                if team_count == 0:
                    team_name = team_a_name
                    opposing_team = team_b_name
                else:
                    team_name = team_b_name
                    opposing_team = team_a_name
                try:
                    write_team_data_to_file(team_name=team_name, players=player_names, 
                        opposing_team=opposing_team, map_name='None', map_pick='None',
                        starting_side='None', map_result='None', 
                        scoreline=f'{0}:{0}', overtime_flag=False,
                        match_length='00:00', date_of_match=date_of_match, event_name=event_name, vod_link='None')
                    continue
                except:
                    print(f"Failed to write unplayed team data on line: {matchup_count+1}\n")
                    with open('error.txt', 'a') as infile:
                        infile.write(f"Failed to write unplayed team data on line: {matchup_count+1}\n")
                    continue

            for i, map in enumerate(maps):
                # Check to avoid adding unplayed maps
                if i+1 > integer_scoreline:
                    continue
                
                map_player_names = []
                map_player_names = player_names.copy()
                if map['map_length'] != '-':
                    # Check if player played on map
                    for player in team['players']:
                        if player['matches'][i]['agent'] == 'None':
                            map_player_names.remove(player['player_name'])
                else:
                    for player in team['players']:
                        try:
                            player_idx = map_player_names.index(team['players'][-1]['player_name'])
                            map_player_names.remove(team['players'][-1]['player_name'])
                        except:
                            pass
                        if 5 > len(map_player_names):
                            map_player_names.insert(player_idx, team['players'][-1]['player_name'])
                            break
                        else:
                            continue
                # Set vod link for map
                vod_link = map['vod_link']

                # Flag to know which scoreline is team's
                team_is_a = False

                # Flag to check for overtime
                overtime_flag = False

                # Set match time length
                match_length = map['map_length']

                # Set map name and picked by
                map_name = map['map_name']
                # If last map, it's a decider
                if i+1 == int(matchup_data['format'][-1]):
                    map_pick = 'Decider'
                else:
                    map_pick = map['picked_by']

                # Verify which team is which
                if team_name == team_a_name:
                    opposing_team = team_b_name
                    team_is_a = True
                else:
                    opposing_team = team_a_name
                
                # Check for overtime
                if map['scoreline']['overtime']['team_a'] > 0 or map['scoreline']['overtime']['team_b'] > 0:
                    overtime_flag = True

                # Evaluate the result of the map
                (map_result, starting_side, 
                 team_score, opposing_score) = evaluate_map_result(map, team_is_a)
                
                try:
                    write_team_data_to_file(team_name=team_name, players=map_player_names, 
                                            opposing_team=opposing_team, map_name=map_name, map_pick=map_pick,
                                            starting_side=starting_side, map_result=map_result, 
                                            scoreline=f'{team_score}:{opposing_score}', overtime_flag=overtime_flag,
                                            match_length=match_length, date_of_match=date_of_match, event_name=event_name, vod_link=vod_link)
                except:
                    print(f"Failed to write team on line: {matchup_count+1}, Team name: {team_name}, Opposition: {opposing_team} on {map_name}\n")
                    with open('error.txt', 'a') as infile:
                        infile.write(f"Failed to write team on line: {matchup_count+1}, Team name: {team_name}, Opposition: {opposing_team} on {map_name}\n")

        print(f"Finished matchup num: {matchup_count+1}")        

# Profiling #
if __name__=='__main__':
    import cProfile
    import pstats

    with cProfile.Profile() as pr:
        main()
    
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats() # Print The Stats
    stats.dump_stats("stats.prof") # Dump to file