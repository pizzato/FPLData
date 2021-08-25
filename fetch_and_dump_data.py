from datetime import datetime
from fpldata import FPLData
import os
import pickle

# Secrets
MANAGERS = []  # List of managers IDs
LEAGUES = []  # List of league IDs
MYTEAM = None  # Your own manager ID
EMAIL = None  # FPL Login Email
PASSWORD = None  # FPL Login Password

now = datetime.now().strftime("%Y%m%d-%H%M%S")
FOLDER = 'data/{now}/'.format(now=now)
FN_PREFIX = 'fpldata_'

def fetch_and_dump():
    fd = FPLData(convert_to_dataframes=True)

    file_append_str = '_{now}'.format(now=now)
    os.makedirs(FOLDER)

    print("Getting Info")
    info_pkl = fd.fetch_info()
    with open(FOLDER + FN_PREFIX + 'info' + file_append_str + '.pkl', 'wb') as f:
        pickle.dump(info_pkl, f)


    print("Getting Fixtures")
    fixtures_df = fd.fetch_fixtures()
    fixtures_df.to_csv(FOLDER + FN_PREFIX + 'fixtures' + file_append_str + '.csv')
    fixtures_df.to_pickle(FOLDER + FN_PREFIX + 'fixtures' + file_append_str + '.pkl')

    print("Getting Elements")
    elements_pkl = fd.fetch_elements(element_ids=fd.data['info']['elements'].id)
    with open(FOLDER + FN_PREFIX + 'elements' + file_append_str + '.pkl', 'wb') as f:
        pickle.dump(elements_pkl, f)

    print("Getting Game Week")
    game_week_pkl = fd.fetch_game_week()
    with open(FOLDER + FN_PREFIX + 'game_week' + file_append_str + '.pkl', 'wb') as f:
        pickle.dump(game_week_pkl, f)

    if len(MANAGERS) > 0:
        print("Getting Managers")
        managers_pkl = fd.fetch_managers(manager_ids=MANAGERS)
        with open(FOLDER + FN_PREFIX + 'managers' + file_append_str + '.pkl', 'wb') as f:
            pickle.dump(managers_pkl, f)

        print("Getting Managers History")
        managers_history_pkl = fd.fetch_managers_history(manager_ids=MANAGERS)
        with open(FOLDER + FN_PREFIX + 'managers_history' + file_append_str + '.pkl', 'wb') as f:
            pickle.dump(managers_history_pkl, f)

    if len(LEAGUES) > 0:
        print("Getting Leagues")
        leagues_pkl = fd.fetch_leagues(league_ids=LEAGUES, get_all_standings=False)
        with open(FOLDER + FN_PREFIX + 'leagues' + file_append_str + '.pkl', 'wb') as f:
            pickle.dump(leagues_pkl, f)

    if (MYTEAM is not None) and (EMAIL is not None and PASSWORD is not None):
        print("Getting My TEAM")
        my_team_pkl = fd.fetch_my_team(my_team = MYTEAM, email=EMAIL, password=PASSWORD)
        with open(FOLDER + FN_PREFIX + 'my_team' + file_append_str + '.pkl', 'wb') as f:
            pickle.dump(my_team_pkl, f)



if __name__ == "__main__":
    fetch_and_dump()