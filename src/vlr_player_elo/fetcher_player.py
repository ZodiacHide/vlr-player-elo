import os
import time
import sqlite3
import requests
from bs4 import BeautifulSoup
from vlr_player_elo.setters_db import insert_player
from tools.tools import write_error_to_file, find_data_directory
from tools.fetcher_base import Fetcher

class PlayerData(Fetcher):
    def __init__(self, base_url: str) -> None:
        super().__init__(base_url)
        
    def fetch_player_data(self, id:int) -> tuple:
        player_url = f'{self.base_url}/player/{id}'
        self.id = id

        # Send GET request
        response = requests.get(player_url, timeout=5)
        try:
            response.raise_for_status()
            assert response.status_code == 200, f"Connection failed to {player_url}. Status code: {response.status_code}"
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
        parsed_page = BeautifulSoup(response.content, 'html.parser')
        player_header = parsed_page.find('div', class_=['player-header'])
        # Find alias
        try:
            player_alias_header = player_header.find('h1', class_=['wf-title'])
            self.player_alias = player_alias_header.get_text(strip=True)
            assert isinstance(self.player_alias, str), f"player_id : {self.id}, 'player_alias' must be of type 'str', but got {type(self.player_alias).__name__}"
            try:
                assert len(self.player_alias) > 0, f"player_id : {self.id}, 'player_alias' is an empty string"
            except AssertionError as e:
                print(f"Assertion length error: {e}")
                write_error_to_file('insert_player_error', e)
                return None
        except Exception as e:
            write_error_to_file('unexpected_error', e)
            print(f"Unexpected error: {e}")
        # Find real name
        try:
            player_real_name_header = player_header.find('h2', class_=['player-real-name'])
            self.player_real_name = player_real_name_header.get_text(strip=True)
            assert isinstance(self.player_real_name, str), f"player_id : {self.id}, 'player_real_name' must be of type 'str', but got {type(self.player_real_name).__name__}"
            try:
                assert len(self.player_real_name) > 0, f"player_id : {self.id}, 'player_real_name' is an empty string"
            except AssertionError as e:
                print(f"Assertion length error: {e}")
                write_error_to_file('insert_player_error', e)
                self.player_real_name = None
        except Exception as e:
            write_error_to_file('unexpected_error', e)
            print(f"Unexpected error: {e}")
        # Find player country
        try:
            player_country_div = player_header.find('div', class_=['ge-text-light'])
            self.player_country = player_country_div.get_text(strip=True)
            assert isinstance(self.player_country, str), f"player_id : {self.id}, 'player_country' must be of type 'str', but got {type(self.player_country).__name__}"
            try:
                assert len(self.player_country) > 0, f"player_id : {self.id}, 'player_country' is an empty string"
            except AssertionError as e:
                write_error_to_file('insert_player_error', e)
                print(f"Assertion length error: {e}")
                self.player_country = None
        except Exception as e:
            write_error_to_file('unexpected_error', e)
            print(f"Unexpected error: {e}")
        
        return self.id, self.player_alias, self.player_country, self.player_real_name
    
    def find_last_player_id_in_db(self):
        # Path to the db
        db_path = os.path.join(find_data_directory(), 'valorant.db')
        try: 
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            try:
                # Get last player_id by desc order
                cursor.execute(f'SELECT * FROM players ORDER BY player_id DESC LIMIT 1;')
                last_id = cursor.fetchone()[0]
                if last_id:
                    return last_id
            except Exception as e:
                print(f"Unexpected error: {e}")
        finally:
            if conn:
                conn.close()
            else:
                raise ConnectionError(f"Unable to establish connection to {db_path}")
    
def main():
    base_url = 'https://www.vlr.gg'
    inst = PlayerData(base_url=base_url)
    last_id = inst.find_last_player_id_in_db()
    if last_id:
        for i in range(last_id+1, 50000):
            PLAYER_DATA = inst.fetch_player_data(i)
            if PLAYER_DATA is not None:
                insert_player(*PLAYER_DATA)
if __name__=='__main__':
    main()