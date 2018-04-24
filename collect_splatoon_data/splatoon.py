import requests
import json
import sys

AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR'
SPLATOON2_FESTIVAL_MATCH_RANKING_URI = 'https://app.splatoon2.nintendo.net/api/festivals/{}/rankings'
SPLATOON2_FESTIVAL_HISTORY_URI = 'https://app.splatoon2.nintendo.net/api/festivals/pasts'
SPLATOON2_LEAGUE_MATCH_RANKING_URI = 'https://app.splatoon2.nintendo.net/api/league_match_ranking/{}/JP'

class SplatoonClient:
    def __init__(self,iksm_session=None):
        if not iksm_session:
            if os.getenv("IKSM_SESSION"):
                self.iksm_session = os.getenv("IKSM_SESSION")
            else:
                print("error: environment variable of IKSM_SESSION is required")
                sys.exit(1)
        else:
            self.iksm_session=iksm_session

        self.cookies = dict(iksm_session=self.iksm_session)
           
    def get_festival_ranking(self,fes_uri_part):
        return self._get_splatoon_request(SPLATOON2_FESTIVAL_MATCH_RANKING_URI.format(fes_uri_part)).text
    
    def get_festival_list(self):
        return self._get_splatoon_request(SPLATOON2_FESTIVAL_HISTORY_URI).json()
    
    def get_league_ranking(self, match_date_uri):
        return self._get_splatoon_request(SPLATOON2_LEAGUE_MATCH_RANKING_URI.format(match_date_uri)).text
    
    def _get_splatoon_request(self, url):
        r = requests.get(url, cookies=self.cookies)
        if r.status_code == 403 and r.json().get('code') == AUTHENTICATION_ERROR:
            print("error: authentication error. make sure your iksm_session.")
            sys.exit(1)
        return r
