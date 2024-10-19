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
        """Sets parsed page data"""
        response = self._connect()
        parsed_page = BeautifulSoup(response.content, 'html.parser')
        self.parsed_page = parsed_page

    def _find_team_IDs(self) -> None:
        """Sets team IDs as *int* *np.ndarray*"""
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
        """Sets game ids as *list* of *int*, sets *list* for each map container and sets all maps container."""
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
        """Returns the *int* ID of player"""
        table_data = row.find('td', class_='mod-player')
        player_ref = table_data.find('a', href=True)
        player_link_str = player_ref['href']
        player_link_str = player_link_str.split('/')
        player_id = int(player_link_str[2])
        return player_id
    
    def _find_player_agent(self, row) -> str:
        """Returns the name of played agent"""
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
        """Returns a tuple containing the kills, deaths and assists data"""
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
        """Returns a tuple containing the first kills and first deaths data"""
        kill_data = row.find('td', class_="mod-stat mod-fb")
        death_data = row.find('td', class_="mod-stat mod-fd")
        data_list = [kill_data, death_data]
        for i, data in enumerate(data_list):
            data_str = data.find('span', class_='mod-both').get_text()
            data_int = int(data_str)
            data_list[i] = data_int   
        return tuple(data_list)
    
    def _find_event_name(self) -> None:
        """Sets the event name as *str*"""
        self.match_header_sup = self.match_header_vs.find_previous_sibling('div', class_='match-header-super')
        header_sup_a = self.match_header_sup.find('a', href=True)
        self.event_name = header_sup_a.find('div', attrs={'style':True}).get_text().strip()

    def _find_date_time_played(self) -> None:
        """Sets the date played and time played as *str*"""
        match_header_date = self.match_header_sup.find('div', class_='match-header-date')
        date_played_div = match_header_date.find_next('div')
        time_played_div = date_played_div.find_next('div')
        self.date_played = date_played_div.get_text().strip()
        self.time_played = time_played_div.get_text().strip()

    def _find_series_format(self) -> None:
        "Sets the series format as a *str*"
        self.header_vs_score = self.match_header_vs.find('div', class_='match-header-vs-score')
        header_vs_score_notes = self.header_vs_score.find_all('div', class_='match-header-vs-note')
        series_format_str = header_vs_score_notes[-1].get_text().strip()
        self.series_format = series_format_str.upper()
    
    def _find_team_scores(self) -> None:
        """Sets the team scores as a *list* of *int*"""
        scoreline_div = self.header_vs_score.find('div', class_='js-spoiler')
        score_span = scoreline_div.find_all('span')
        team1_score = int(score_span[0].get_text())
        team2_score = int(score_span[-1].get_text())
        self.team_score = [team1_score, team2_score]
    
    def _find_game_length(self) -> None:
        """Sets game duration as a *list* of *str*"""
        self.game_duration = np.zeros(len(self.individual_maps), dtype=object)
        for i, map in enumerate(self.individual_maps):
            map_header = map.find('div', class_='vm-stats-game-header')
            game_duration_div = map_header.find('div', class_='map-duration ge-text-light')
            self.game_duration[i] = game_duration_div.get_text().split()[0]
    
    def _find_map_name_and_pick_by(self) -> None:
        self.picked_by = np.zeros(len(self.individual_maps))
        self.map_name = np.zeros(len(self.individual_maps), dtype=object)
        for m, map in enumerate(self.individual_maps):
            map_div = map.find('div', class_='map')
            map_span = map_div.find('span')
            self.map_name[m] = map_span.get_text().split()[0]
            daughter_map_span = map_span.find('span')
            if daughter_map_span is not None:
                span_classes = daughter_map_span['class']
                span_mod = span_classes[1]
                if span_mod[-1].isdigit():
                    digit = int(span_mod[-1])
                    if digit == 2:
                        self.picked_by[m] = self.team_id[1]
                    else:
                        self.picked_by[m] = self.team_id[0]
                else:
                    ...
                    # Some error
            else:
                self.picked_by[m] = -1
    
    def _find_fh_sh_score(self) -> None:
        self.fhsh_score = np.zeros((2, len(self.individual_maps), 2))
        self.fh_sides = np.zeros((2, len(self.individual_maps)), dtype=object)
        for m, map in enumerate(self.individual_maps):
            game_header = map.find('div', class_='vm-stats-game-header')
            team_header_score = game_header.find_all('div', class_='team')
            for i, team_header in enumerate(team_header_score):
                score_span = team_header.find_all('span')
                self.fh_sides[i, m] = score_span[0]['class'][0].split('-')[-1]
                fh_score = int(score_span[0].get_text().strip())
                sh_score = int(score_span[1].get_text().strip())
                self.fhsh_score[i,m,:] = fh_score, sh_score
    
    def _find_fh_sh_pistol_winner(self) -> None:
        """Sets first half and second half pistol winner sides (CT/T)"""
        self.fhsh_pistol_winner = np.zeros((len(self.individual_maps), 2), dtype=object)
        for m, map in enumerate(self.individual_maps):
            vlr_rounds = map.find('div', class_='vlr-rounds-row')
            vlr_columns = vlr_rounds.find_all('div', class_='vlr-rounds-row-col')
            fh_pistol_div = vlr_columns[1]
            fh_pistol_winner_container = fh_pistol_div.find_all('div', class_='rnd-sq')
            for container in fh_pistol_winner_container:
                if len(container['class']) < 2:
                    continue
                else:
                    fh_pistol_winner = container['class'][-1].split('-')[-1]
            # skip 11 rounds + spacer
            sh_pistol_div = vlr_columns[14]
            sh_pistol_winner_container = sh_pistol_div.find_all('div', class_='rnd-sq')
            for container in sh_pistol_winner_container:
                if len(container['class']) < 2:
                    continue
                else:
                    sh_pistol_winner = container['class'][-1].split('-')[-1]
            self.fhsh_pistol_winner[m,:] = fh_pistol_winner, sh_pistol_winner
    
    def _find_vod_link(self) -> None:
        match_vods_container = self.parsed_page.find('div', class_='match-vods')
        streams_container = match_vods_container.find('div', class_='match-streams-container')
        vod_refs = streams_container.find_all('a', href=True)
        self.vod_link = ''
        for i, vod in enumerate(vod_refs):
            if i != len(vod_refs)-1:
                self.vod_link += vod['href'] + ', '
            else:
                self.vod_link += vod['href']

    def fetch_all_data(self):
        self._find_team_IDs()
        self._find_match_table()
        self._find_player_data()
        self._find_event_name()
        self._find_date_time_played()
        self._find_series_format()
        self._find_team_scores()
        self._find_game_length()
        self._find_map_name_and_pick_by()
        self._find_fh_sh_score()
        self._find_fh_sh_pistol_winner()
        self._find_vod_link()

    def write_to_db(self) -> None:
        for g, game in enumerate(self.player_data):
            ### Write player data to player_performance ###
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
                # setters_db.insert_player_performance(*arr)
            ### Write game data to games ###
            arr = np.zeros(14, dtype=object)
            arr[0] = int(self.game_ids[g])
            arr[1] = int(self.series_id)
            arr[2] = self.map_name[g]
            arr[3] = int(self.picked_by[g])
            arr[4], arr[7] = int(self.team_id[0]), int(self.team_id[1])
            arr[5], arr[6] = int(self.fhsh_score[0][g][0]), int(self.fhsh_score[0][g][1])
            arr[8], arr[9] = int(self.fhsh_score[1][g][0]), int(self.fhsh_score[1][g][1])
            for i, winner in enumerate(self.fhsh_pistol_winner[g]):
                if winner == self.fh_sides[0][g]:
                    # If it's the second half, and same side won
                    # That means other team won
                    if i != 1:
                        arr[10+i] = int(self.team_id[0])
                    else:
                        arr[10+i] = int(self.team_id[1])
                elif winner == self.fh_sides[1][g]:
                    if i != 1:
                        arr[10+i] = int(self.team_id[1])
                    else:
                        arr[10+i] = int(self.team_id[0])

            arr[12] = self.vod_link
            arr[13] = self.game_duration[g]
            print(arr)
            setters_db.insert_game(*arr)

        ### Write series data to series ###
        arr = np.zeros(9+len(self.player_data), dtype=object)
        arr[0] = int(self.series_id)
        arr[1], arr[2] = int(self.team_id[0]), int(self.team_id[1])
        arr[3] = self.event_name
        arr[4] = self.date_played
        arr[5] = self.time_played
        arr[6] = self.series_format
        arr[7], arr[8] = self.team_score
        for g in range(len(self.player_data)):
            arr[9+g] = self.game_ids[g]
        setters_db.insert_series(*arr)

        ### Write and/or update data to team ###
        

def main():
    init = SeriesData(base_url='https://www.vlr.gg', series_id='412600')
    init.fetch_all_data()
    init.write_to_db()

if __name__=='__main__':
    main()