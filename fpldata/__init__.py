import json

import requests
import pandas as pd
import numpy as np

# Base URLs

_EP_BASE = "https://fantasy.premierleague.com/api/"
_EP_INFO = _EP_BASE + "bootstrap-static/"
_EP_FIXTURES = _EP_BASE + "fixtures/"
_EP_ELEMENT = _EP_BASE + "element-summary/{element_id}/"
_EP_GAMEWEEK = _EP_BASE + "event/{game_week}/live/"
_EP_MANAGER = _EP_BASE + "entry/{manager_id}/"
_EP_MANAGER_HISTORY = _EP_BASE + "entry/{manager_id}/history"
_EP_LEAGUE_STANDING = _EP_BASE + "leagues-classic/{league_id}/standings?page_standings={page}"
_EP_MYTEAM = _EP_BASE + "my-team/{team_id}/"
_EP_TRANSFERS = _EP_BASE + "transfers/"
_EP_LOGIN = "https://users.premierleague.com/accounts/login/"
_EP_LOGIN_REDIRECT = "https://fantasy.premierleague.com/"
_MAX_GAME_WEEKS = 38


def get_headers(referer): #from fpl
    """Returns the headers needed for the transfer request."""
    return {
        "Accept": "*/*",
        "Content-Type": "application/json;",
        "X-Requested-With": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
        "Referer": referer
    }

def serialize_int64(obj):
    if isinstance(obj, np.int64):
        return int(obj)
    raise TypeError ("Type %s is not serializable" % type(obj))

class FPLData:
    """
    FPLData class that fetches data from FPL API and stores in a dictionary structure or pandas data frames.

        Data is return on each function and also stored in self.data
    """
    def __init__(self, convert_to_dataframes:bool=True, force_dataframes:bool=False, pl_profile_cookie=None):
        """

        :param convert_to_dataframes: boolean indicating that the data when possible will be converted to dataframes (default: True)
        :param force_dataframes: boolean indicating that non optimal dataframes such as simple vars are also converted to dataframes (default: False)
        """
        self._convert_to_dataframes = convert_to_dataframes
        self._force_dataframes = force_dataframes

        self.data = {}

        self.session = requests.Session()
        self.set_pl_profile_cookie(pl_profile_cookie=pl_profile_cookie)

    def set_pl_profile_cookie(self, pl_profile_cookie):
        self.pl_profile_cookie = pl_profile_cookie
        self.session.cookies.set(name='pl_profile',
                                 value=pl_profile_cookie)

    def fetch(self,
              info=True, fixtures=False, elements: list = None, game_week=False,
              managers: list = None, manager_history=False,
              leagues: list = None, all_standings=False
              ):
        """

        :param info:
        :param fixtures:
        :param elements:
        :param game_week:
        :param managers:
        :param manager_history:
        :param leagues:
        :param all_standings:
        :return: dict
        """

        if info:
            self.fetch_info()

        if fixtures:
            self.fetch_fixtures()

        if elements:
            self.fetch_elements(element_ids=elements)

        if game_week:
            self.fetch_game_week()

        if managers:
            self.fetch_managers(manager_ids=managers)

        if manager_history:
            self.fetch_managers_history(manager_ids=managers)

        if leagues:
            self.fetch_leagues(league_ids=leagues, get_all_standings=all_standings)

    def fetch_info(self):
        """
        Fetches info
        :return: dict
        """

        data_ = self.session.get(_EP_INFO).json()

        if self._convert_to_dataframes:
            for k in data_.keys():
                if k in ['events', 'phases', 'teams', 'elements', 'element_types']:
                    data_[k] = pd.DataFrame(data_[k])
                elif self._force_dataframes:
                    try:
                        data_[k] = pd.DataFrame([data_[k]]).T
                    except ValueError:
                        pass

        self.data['info'] = data_
        return data_



    def fetch_fixtures(self):
        """
        Fetches fixture info
        :return: dict
        """

        data_ = self.session.get(_EP_FIXTURES).json()
        if self._convert_to_dataframes:
            data_ = pd.DataFrame(data_)

        self.data['fixtures'] = data_
        return data_

    def fetch_elements(self, element_ids: list):
        """
        Fetches info for all elements (players) in list
        :param element_ids: list of element ids (players)
        :return: dict
        """

        data_ = {}
        for element_id in element_ids:
            dt_json = self.session.get(_EP_ELEMENT.format(element_id=element_id)).json()

            data_[element_id] = dt_json \
                if not self._convert_to_dataframes \
                else {k: pd.DataFrame(dt_json[k]) for k in dt_json.keys()}

        self.data['elements'] = data_
        return data_

    def fetch_game_week(self):
        """
        Fetches all games weeks elements
        :return: dict
        """

        data_ = {}

        for gw in range(1, _MAX_GAME_WEEKS+1):
            dt_json = self.session.get(_EP_GAMEWEEK.format(game_week=gw)).json()

            data_[gw] = dt_json['elements'] \
                if not self._convert_to_dataframes \
                else pd.DataFrame(dt_json['elements'])

        self.data['game_week_elements'] = data_
        return data_

    def fetch_managers(self, manager_ids: list):
        """
        Fetches managers info
        :param manager_ids: list of ids for managers to get info
        :return: dict
        """

        data_ = {}

        for manager_id in manager_ids:
            dt_json = self.session.get(_EP_MANAGER.format(manager_id=manager_id)).json()

            data_[manager_id] = dt_json \
                if not self._convert_to_dataframes \
                else pd.DataFrame(dt_json)

        self.data['manager_id'] = data_
        return data_

    def fetch_managers_history(self, manager_ids: list):
        """
        Fetches managers history
        :param manager_ids: list of ids for managers to get info
        :return: dict
        """

        data_ = {}

        for manager_id in manager_ids:
            dt_json = self.session.get(_EP_MANAGER_HISTORY.format(manager_id=manager_id)).json()

            data_[manager_id] = dt_json \
                if not self._convert_to_dataframes \
                else {k: pd.DataFrame(dt_json[k]) for k in dt_json.keys()}

        self.data['manager_id_history'] = data_
        return data_

    def fetch_leagues(self, league_ids: list, get_all_standings=False):
        """
        Fetches leagues standings and other information
        :param league_ids: list of ids for all leagues to get standings
        :param get_all_standings: if there is pagination (many players), whether to get them all (default: False)
        :return: dict
        """

        data_ = {}

        for league_id in league_ids:
            dt_json = self.session.get(_EP_LEAGUE_STANDING.format(league_id=league_id, page=1)).json()

            data_[league_id] = dt_json
            data_[league_id]['new_entries'] = dt_json['new_entries']['results']
            data_[league_id]['standings'] = dt_json['standings']['results']

            if get_all_standings:
                while dt_json['standings']['has_next']:
                    dt_json = self.session.get(_EP_LEAGUE_STANDING.format(league_id=league_id, page=int(
                        dt_json['standings']['has_next']) + 1)).json()

                    data_[league_id]['standings'] += dt_json['standings']['results']

            if self._convert_to_dataframes:
                data_[league_id]['standings'] = \
                    pd.DataFrame(data_[league_id]['standings'])
            if self._force_dataframes:
                data_[league_id]['league'] = \
                    pd.DataFrame([data_[league_id]['league']]).T

        self.data['league_id'] = data_
        return data_

    def fetch_my_team(self, my_team, email=None, password=None):
        """
        Featch information about your team using email and password (not working with email and password, use cookie)

        :param my_team: team_id
        :param email: email
        :param password: password
        :return: dict
        """

        if email is not None and password is not None:
            headers = {
                'authority': 'users.premierleague.com',
                'origin': 'https://fantasy.premierleague.com',
                'content-type': 'application/x-www-form-urlencoded',
                'user-agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1; PRO 5 Build/LMY47D)',
                #'accept': 'text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7;',
                'referer': 'https://fantasy.premierleague.com/',
                'accept-language': 'en-AU,en-GB;q=0.9,en;q=0.8,en-US;q=0.7',
                'accept-encoding': 'gzip, deflate, br'
            }

            payload = {
                'login': email,
                'password': password,
                'app': 'plfpl-web',
                'redirect_uri': _EP_LOGIN_REDIRECT
            }

            _ = self.session.post(_EP_LOGIN, data=payload, headers=headers)

        data_ = self.session.get(_EP_MYTEAM.format(team_id=my_team)).json()

        if self._convert_to_dataframes:
            for k in ['picks', 'chips']:
                data_[k] = pd.DataFrame(data_[k])

            if self._force_dataframes:
                data_['transfers'] = pd.DataFrame([data_['transfers']]).T

        self.data['my_team'] = data_
        return data_

    def transfer(self, my_team, event, elements_in, elements_out):
        elements_in = sorted(elements_in)
        elements_out = sorted(elements_out)

        df_team_picks = self.fetch_my_team(my_team=my_team)['picks']
        selling_price = df_team_picks[df_team_picks['element'].isin(elements_out)].sort_values('element')['selling_price'].tolist()

        df_elements = self.fetch_info()['elements']
        #purchase_price = df_elements[df_elements['code'].isin(elements_in)]['now_cost'].tolist()
        purchase_price = df_elements[df_elements['id'].isin(elements_in)].sort_values('id')['now_cost'].tolist()

        payload = dict(chip=None, entry=my_team, event=event)

        #element in and out must be of same type, this code should be improved
        element_in_type = df_elements[df_elements['id'].isin(elements_in)].sort_values('id')['element_type'].tolist()
        element_out_type = df_elements[df_elements['id'].isin(elements_out)].sort_values('id')['element_type'].tolist()

        d_elem_in = [dict(eid=eid, pp=pp, et=et) for eid, pp, et in zip(elements_in, purchase_price, element_in_type)]
        d_elem_out = [dict(eid=eid, sp=sp, et=et) for eid, sp, et in zip(elements_out, selling_price, element_out_type)]

        d_elem_in_out = []
        for elem_in in d_elem_in:
            while len(d_elem_out) > 0:
                elem_out = d_elem_out.pop(0)
                if elem_out['et'] != elem_in['et']:
                    d_elem_out.append(elem_out)
                else:
                    break
            d_elem_in_out.append((elem_in, elem_out))

        payload['transfers'] = [dict(element_in=elem_in['eid'], element_out=elem_out['eid'], purchase_price=elem_in['pp'], selling_price=elem_out['sp'])
                                for elem_in, elem_out in d_elem_in_out]

        # {"chip": null, "entry": 4950591, "event": 1,
        #  "transfers": [{"element_in": 275, "element_out": 482, "purchase_price": 45, "selling_price": 45}]}
        print(payload)
        print(json.dumps(payload, default=serialize_int64))

        r = self.session.post(_EP_TRANSFERS, data=json.dumps(payload, default=serialize_int64), headers=get_headers('https://fantasy.premierleague.com/transfers'))

        return r

    def pick_team(self, my_team):
        """
        Featch information about your team using email and password (not working with email and password, use cookie)

        :param my_team: team_id
        :return: dict
        """

        df_team_picks = self.fetch_my_team(my_team=my_team)['picks']

        df_elements = self.fetch_info()['elements']
        df_team_info = df_elements[df_elements.id.isin(df_team_picks.element)]

        pick_pos_pos = [[1], # 1, GK
                        [2], [2], [2], # 2, 3, 4: DEF
                        [2, 3], #5 : DF, MID
                        [3], [3], [3], # 6, 7, 8: MID
                        [3, 4], [3, 4],# 9, 10: MID, FRW
                        [4], # 11: FRW
                        [1], # 12: GK (Sub)
                        [2, 3], # 13: DF, MID (Sub)
                        [2, 3, 4], # 14: DF, MID, FRW (Sub)
                        [3, 4] # 15: MID, FRW (Sub)
                        ]
        sort_columns = ['ep_next', 'total_points', 'now_cost']


        picks_list = []
        for accept_pos in pick_pos_pos:
            element_pick = df_team_info[df_team_info.element_type.isin(accept_pos) &
                                        ~df_team_info['id'].isin(picks_list)].sort_values(sort_columns,
                                                                                     ascending=False)['id'].iloc[0]
            picks_list.append(element_pick)

        captain = df_team_info.sort_values(sort_columns, ascending=False).iloc[0]
        vicecaptain = df_team_info[(df_team_info['id'] != captain['id']) &
                                   (df_team_info['team'] != captain['team'])].sort_values(sort_columns,
                                                                                          ascending=False).iloc[0]

        picks = [
            dict(element=pe,
                 is_captain=bool(pe == captain['id']),
                 is_vice_captain=bool(pe == vicecaptain['id']),
                 position=p+1)
            for p, pe in enumerate(picks_list)
        ]

        payload = {'chip': None,'picks': picks}
        print(payload)

        print(json.dumps(payload, default=serialize_int64))

        r = self.session.post(_EP_MYTEAM.format(team_id=my_team), data=json.dumps(payload, default=serialize_int64), headers=get_headers('https://fantasy.premierleague.com/my-team'))

        return r
