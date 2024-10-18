from tools.fetcher_base import Fetcher
from vlr_player_elo import setters_db
from typing import Union
from bs4 import BeautifulSoup
import requests
import time
import numpy as np

class SeriesData(Fetcher):
    def __init__(self, base_url:str, series_id:str) -> None:
        super().__init__(base_url)
        if not isinstance(series_id, str):
            if isinstance(series_id, (int, float)):
                self.series_id = str(int(series_id))
            else:
                raise TypeError(f"'series_id' must be of type 'str', but got {type(self.series_id).__name__}")
        else:
            self.series_id = series_id
        self.series_url = base_url + '/' + self.series_id

        # Instance methods
        self._get_parsed_page()
        self._find_team_IDs()
        self._find_match_table()
        self._find_player_data()

    def _connect(self) -> Union[requests.Response, None]:
        # Send GET request
        response = requests.get(self.series_url, timeout=5)
        try:
            response.raise_for_status()
            assert response.status_code == 200, f"Connection failed to {self.series_url}. Status code: {response.status_code}"
            # Avoid overloading website
            time.sleep(1)
        except AssertionError as e:
            print(f"Assertion connection error: {e}")
            return None
        except requests.exceptions.Timeout as e:
            print(f"Connection timed out: {e}")
            return None
        except requests.exceptions.HTTPError as e:
            print(f"Connection error: {e}")
            return None
        
        return response

    def _get_parsed_page(self) -> None:
        response = self._connect()
        parsed_page = BeautifulSoup(response.content, 'html.parser')
        self.parsed_page = parsed_page

    def _find_team_IDs(self) -> None:
        self.match_header_vs = self.parsed_page.find('div', class_='match-header-vs')
        team_link_a = self.match_header_vs.find_all('a', href=True)
        team_links = []
        for ref in team_link_a:
            team_links.append(ref['href'])
        
        team_id = np.zeros(2, dtype=int)
        for i, href in enumerate(team_links):
            # Inidices 0: None, 1: 'team', 2: team_id, 3: team_name
            href = href.split('/')
            team_id[i] = href[2]
        
        self.team_id = team_id

    def _find_match_table(self) -> None:
        # Find the entire table
        match_table = self.parsed_page.find('div', class_='vm-stats-container')
        # Individual map table, also includes 'all'
        maps_tables = match_table.find_all('div', attrs={'data-game-id':True})
        self.individual_maps = []
        self.game_ids = []
        for div in maps_tables:
            # Filter between all and maps
            data_game_id = div['data-game-id']
            if data_game_id.isdigit():
                self.individual_maps.append(div)
                self.game_ids.append(int(data_game_id))
            else:
                self.all_maps_table = div

    def _find_player_data(self) -> None:
        self.player_data = np.zeros((len(self.individual_maps),10,12), dtype=object)
        for m, _map in enumerate(self.individual_maps):
            # Finding the table for each team
            team_table = _map.find_all('table', class_='wf-table-inset mod-overview')
            for t, team in enumerate(team_table):
                # Finding the body row for each player
                players_body = team.find('tbody')
                players = players_body.find_all('tr')
                for i, player in enumerate(players):
                    ID = self._find_player_id(player)
                    AGENT = self._find_player_agent(player)
                    K, D, A = self._find_player_KDA(player)
                    FK, FD =self._find_player_FKFD(player)
                    RATING, ACS, KAST, ADR, HSP = self._find_player_rating_ACS_KAST_ADR_HSP(player)

                    data_list = [ID, AGENT, RATING, ACS, K, D, A, KAST, ADR, HSP, FK, FD]
                    self.player_data[m,i+(t*5),:] = data_list
           
    def _find_player_id(self, row) -> int:
        table_data = row.find('td', class_='mod-player')
        player_ref = table_data.find('a', href=True)
        player_link_str = player_ref['href']
        player_link_str = player_link_str.split('/')
        player_id = int(player_link_str[2])
        return player_id
    
    def _find_player_agent(self, row) -> str:
        table_data = row.find('td', class_='mod-agents')
        img_data = table_data.find('img')
        agent_name = img_data['title']
        return agent_name

    def _find_player_rating_ACS_KAST_ADR_HSP(self, row) -> tuple:
        """
        ## Returns
        **data_tuple** : *tuple* \\
            Tuple of format (Rating, ACS, KAST, ADR, HSP)"""
        all_table_data = row.find_all('td', class_='mod-stat')
        # Filter out td elements with additional classes
        filtered_mod_data_tds = [td for td in all_table_data if len(td.get('class', [])) == 1]
        data_mod = [1.0, 1, 1.0, 1, 1.0]
        data_tuple = ()
        for i, data in enumerate(filtered_mod_data_tds):
            data_str = data.find('span', class_='mod-both').get_text()
            if isinstance(data_mod[i], int):
                data = int(data_str)
            else:
                if i == 0:
                    data = float(data_str)
                else:
                    data_str = data_str[:-1] # remove '%'
                    data = float(data_str)/100

            # Append to tuple
            data_tuple += (data,)
        return data_tuple

    def _find_player_KDA(self, row) -> tuple:
        kill_data = row.find('td', class_="mod-stat mod-vlr-kills")
        death_data = row.find('td', class_="mod-stat mod-vlr-deaths")
        assist_data = row.find('td', class_="mod-stat mod-vlr-assists")
        data_list = [kill_data, death_data, assist_data]
        for i, data in enumerate(data_list):
            data_str = data.find('span', class_='mod-both').get_text()
            data_int = int(data_str)
            data_list[i] = data_int   
        return tuple(data_list)
    
    def _find_player_FKFD(self, row) -> tuple:
        kill_data = row.find('td', class_="mod-stat mod-fb")
        death_data = row.find('td', class_="mod-stat mod-fd")
        data_list = [kill_data, death_data]
        for i, data in enumerate(data_list):
            data_str = data.find('span', class_='mod-both').get_text()
            data_int = int(data_str)
            data_list[i] = data_int   
        return tuple(data_list)
    
    def _find_event_name(self) -> None:
        self.match_header_sup = self.match_header_vs.find_previous_sibling('div', class_='match-header-super')
        header_sup_a = self.match_header_sup.find('a', href=True)
        self.event_name = header_sup_a.find('div', attrs={'style':True}).get_text()

    def _find_date_time_played(self) -> None:
        match_header_date = self.match_header_sup.find('div', class_='match-header-date')
        date_played_div = match_header_date.find_next('div')
        time_played_div = date_played_div.find_next('div')
        self.date_played = date_played_div.get_text()
        self.time_played = time_played_div.get_text()

    def _find_series_format(self) -> None:
        header_vs_score = self.match_header_vs.find('div', class_='match-header-vs-score')
        header_vs_score_notes = header_vs_score.find_all('div', class_='match-header-vs-note')
        game_format_str = header_vs_score_notes[-1].get_text()
        self.game_format = game_format_str.capitalize()
    
    def _find_team_scores(self) -> None:
        ...
    
    def _find_game_length(self) -> None:
        ...

    def write_to_db(self) -> None:
        ### Write player data to player_performance ###
        for g, game in enumerate(self.player_data):
            for i, player in enumerate(game):
                arr = np.zeros(14, dtype=object)
                arr[0] = player[0]
                arr[1] = self.game_ids[g]
                # Check if player is first or second team.
                if i/5 < 1:
                    arr[2] = int(self.team_id[0])
                else:
                    arr[2] = int(self.team_id[1])
                for j, point in enumerate(player):
                    if j == 0:
                        continue
                    arr[j+2] = point
                # Attempt to write to db
                setters_db.insert_player_performance(*arr)



def main():
    init = SeriesData(base_url='https://www.vlr.gg', series_id='411597')
    init.write_to_db()

if __name__=='__main__':
    main()