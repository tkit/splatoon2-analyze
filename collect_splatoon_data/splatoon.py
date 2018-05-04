import requests
import os
from splatoon_exceptions import ValueError, AuthenticationError

AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR'
SPLATOON2_FESTIVAL_MATCH_RANKING_URI = 'https://app.splatoon2.nintendo.net/api/festivals/{}/rankings'
SPLATOON2_FESTIVAL_HISTORY_URI = 'https://app.splatoon2.nintendo.net/api/festivals/pasts'
SPLATOON2_LEAGUE_MATCH_RANKING_URI = 'https://app.splatoon2.nintendo.net/api/league_match_ranking/{}/JP'
SPLATOON2_SCHEDULE_URI = 'https://app.splatoon2.nintendo.net/api/schedules'


class SplatoonClient:

    def __init__(self, iksm_session=None):
        if not iksm_session:
            if os.getenv("IKSM_SESSION"):
                self.iksm_session = os.getenv("IKSM_SESSION")
            else:
                raise ValueError("iksm_session", "null")
        else:
            self.iksm_session = iksm_session

        self.cookies = dict(iksm_session=self.iksm_session)

    def get_festival_ranking(self, fes_uri_part):
        return self._get_splatoon_request(
            SPLATOON2_FESTIVAL_MATCH_RANKING_URI.format(fes_uri_part)).text

    def get_festival_list(self):
        return self._get_splatoon_request(SPLATOON2_FESTIVAL_HISTORY_URI).json()

    def get_league_ranking(self, match_date_uri):
        return self._get_splatoon_request(
            SPLATOON2_LEAGUE_MATCH_RANKING_URI.format(match_date_uri)).text

    def get_schedules(self):
        return self._get_splatoon_request(SPLATOON2_SCHEDULE_URI).json()

    def _get_splatoon_request(self, url):
        r = requests.get(url, cookies=self.cookies)
        if r.status_code == 403 and r.json().get('code') == AUTHENTICATION_ERROR:
            raise AuthenticationError(self.iksm_session)
        return r
