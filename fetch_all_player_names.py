import requests
from bs4 import BeautifulSoup
import bs4
import time
import numpy as np
from data_struct import get_user_input_on_scraping

def connect(url: str) -> tuple:
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
        return False, response.status_code
    else:
        try:
            content = response.content
            return True, content
        except:
            return False, 0 
        
def parse_html(content: str) -> bs4.BeautifulSoup:
    parsed = BeautifulSoup(content, 'html.parser')
    return parsed

def check_for_team(parsed_html: bs4.BeautifulSoup) -> tuple:
    team_container = parsed_html.find_all('a', attrs={'style': 'display: flex; justify-content: space-between; align-items: center; padding: 15px 20px;'})
    if len(team_container) == 0:
        # Player has no summary, we're not interested
        return False, 0
    
    team_count = len(team_container)
    player_teams = np.zeros(team_count, dtype=object)
    for i, team in enumerate(team_container):
        team_name_tag = team.find('div', attrs={'style': 'font-weight: 500;'})
        team_name = ' '.join(team_name_tag.get_text().split())
        player_teams[i] = team_name

    return True, player_teams
        

def get_player_name(parsed_html: bs4.BeautifulSoup) -> tuple:
    player_alias = parsed_html.find('h1')
    if player_alias == None:
        # Unable to find player_alias
        return False, 0
    try:
        player_name = player_alias.find_next('h2')
    except:
        # Unable to find player alias or name
        return False, 0
    
    if len(player_name.get_text()) == 0:
        # No name, not interested
        return False, 0 

    alias = ' '.join(player_alias.get_text().split())
    name = ' '.join(player_name.get_text().split())
    return True, (alias, name)

def write_to_file(player_id: int, player_alias: str, player_name: str, team_list: list):
    _player_alias = ''.join(player_alias.split())
    path = f'player_names_dupes\\{player_alias}.txt'
    try:
        with open(path, 'a', encoding="utf-8") as infile:
            infile.write(player_alias + ',' + str(player_id) + ',' + player_name + '\n')
            for team_name in team_list:
                infile.write(team_name + '\n')
    except:
        # Failed to write
        with open('write_errors.txt', 'a', encoding="utf-8") as infile:
                infile.write(f'Unable write player: {_player_alias}: {player_id}\n')
        pass   
    
def scraper(start_id: int, player_count: int):
    for id in range(start_id, start_id + player_count):
        # Avoid overloading
        time.sleep(1)
        print(f'Player id: {id}')
        url = f"https://www.vlr.gg/player/{id}"
        answer, content = connect(url=url)
        if not answer:
            if content == 404:
                continue
            for attempt in range(2):
                # Avoid overloading
                time.sleep(1)
                try:
                    answer, content = connect(url=url)
                except:
                    pass
                if answer:
                    break
            if not answer:
                # Couldn't connect
                with open('connection_errors.txt', 'a', encoding="utf-8") as infile:
                    infile.write(f'Unable to connect to {url}\n')
                continue
        
        # Find team name(s) #
        parsed = parse_html(content=content)
        has_team, player_team = check_for_team(parsed_html=parsed)

        if not has_team:
            # No team, not interested
            with open('team_name_errors.txt', 'a', encoding="utf-8") as infile:
                infile.write(f'Unable find team for player_id: {id}\n')
            continue
        
        # Find player alias and name #
        has_name, player_names = get_player_name(parsed_html=parsed)
        if not has_name:
            # No name, not interested
            with open('player_name_errors.txt', 'a', encoding="utf-8") as infile:
                infile.write(f'Unable find name for player_id: {id}\n')
            continue

        write_to_file(player_id=id, player_alias=player_names[0], 
                      player_name=player_names[1], team_list=player_team)
    
    return player_count + start_id
        

def main(begin: int=1):
    player_count = get_user_input_on_scraping()
    if player_count == None:
        exit()
    new_start = scraper(begin, player_count)
    main(new_start+1)

if __name__=='__main__':
    main()