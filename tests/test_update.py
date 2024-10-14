# test_update.py
from vlr_player_elo import update_db, setters_db
from tools.tools import delete_row

def test_update_team_roster_no_error_tuple():
    team_id = int(1337+1e10)
    roster_tuple = ('John', 'Jane', 'Joseph', 'Joseline', 'Jennifer')

    setters_db.insert_team(team_id, '', 'Billy, Jane, Joseline, Jennifer, Boltzmann', test=True)
    update_db.update_team_roster(team_id=team_id, new_roster=roster_tuple)

    delete_row('teams', 'team_id', team_id)

def test_update_team_roster_no_error_list():
    team_id = int(1337+1e10)
    roster_tuple = ['John', 'Jane', 'Joseph', 'Joseline', 'Jennifer']

    setters_db.insert_team(team_id, '', 'Billy, Jane, Joseline, Jennifer, Boltzmann', test=True)
    update_db.update_team_roster(team_id=team_id, new_roster=roster_tuple)

    delete_row('teams', 'team_id', team_id)

def main():
    test_update_team_roster_no_error_tuple()
    test_update_team_roster_no_error_list()

if __name__=='__main__':
    main()