# test_insert_player_and_get_player.py
import sys
import os

# Add src directory to sys.path relative to this file
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from vlr_player_elo import setters_db, getters_db

def main():
    player_id = 2
    alias = 'swag'
    country = 'USA'
    name = 'Braxton Pierce'

    setters_db.insert_player(player_id, alias, country, name)

    player = getters_db.get_player(player_id)
    print(player)


if __name__=='__main__':
    main()