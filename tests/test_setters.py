# test_insert_player_and_get_player.py
import sys
import os
import inspect

# Add src directory to sys.path relative to this file
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from vlr_player_elo import setters_db
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', '..'))
from tools.tools import delete_row

def test_insert_player_no_error_for_same_id():
    player_id = int(1337+1e10)
    filler_count = len(inspect.signature(setters_db.insert_player).parameters)-2
    vars = [player_id] + ['']*filler_count

    setters_db.insert_player(*vars, test=True)
    setters_db.insert_player(*vars, test=True)
    
    delete_row('players', 'player_id', player_id)

def test_insert_team_no_error_for_same_id():
    team_id = int(1337+1e10)
    filler_count = len(inspect.signature(setters_db.insert_team).parameters)-2
    vars = [team_id] + ['']*filler_count

    setters_db.insert_team(*vars, test=True)
    setters_db.insert_team(*vars, test=True)

    delete_row('teams', 'team_id', team_id)

def test_insert_series_no_error_for_same_id():
    series_id = int(1337+1e10)
    team1_id = int(1338+1e10)
    team2_id = int(1339+1e10)
    filler_count = len(inspect.signature(setters_db.insert_series).parameters)-2-6
    vars = [series_id, team1_id, team2_id] + ['']*4 + [0]*filler_count
    
    setters_db.insert_series(*vars, test=True)
    setters_db.insert_series(*vars, test=True)

    delete_row('series', 'series_id', series_id)

def test_insert_map_no_error_for_same_id():
    map_id = int(1337+1e10)
    series_id = int(1337+1e10)
    map_name = ''
    filler_count = len(inspect.signature(setters_db.insert_map).parameters)-2-4
    vars = [map_id, series_id, map_name] + [0]*filler_count + ['']*2
    
    setters_db.insert_map(*vars, test=True)
    setters_db.insert_map(*vars, test=True)

    delete_row('maps', 'map_id', map_id)

###
# Add test for non-int ID
def main():
    test_insert_player_no_error_for_same_id()
    test_insert_team_no_error_for_same_id()
    test_insert_series_no_error_for_same_id()
    test_insert_map_no_error_for_same_id()

if __name__=='__main__':
    main()