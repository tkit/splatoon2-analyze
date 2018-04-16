"""
Splatoon2のフェスマッチランキングの結果を取得し、jsonファイルで保存するスクリプト
初回から全ての結果を取得する(既に取得済みのものは再取得しない)

環境変数IKSM_SESSIONに各自のiksm_sessionを設定しておく必要あり

usage: python get_festival_ranking.py 
"""

import requests
import json
import time
import random
import progressbar
import os
import sys
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=+9), 'JST')
SPLATOON2_FESTIVAL_MATCH_RANKING_URI = 'https://app.splatoon2.nintendo.net/api/festivals/{}/rankings'
MIN_SLEEP_SEC = 2
MAX_SLEEP_SEC = 5
AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR'

FES_URI_MAP=[
  {
    "fes_no":1,
    "uri_part": "1051"
  },
  {
    "fes_no":2,
    "uri_part": "1052"
  },
  {
    "fes_no":3,
    "uri_part": "1054"
  },
  {
    "fes_no":4,
    "uri_part": "1055"
  },
  {
    "fes_no":5,
    "uri_part": "1056"
  },
  {
    "fes_no":6,
    "uri_part": "4051"
  },
  {
    "fes_no":7,
    "uri_part": "1057"
  },
  {
    "fes_no":8,
    "uri_part": "1058"
  },
  {
    "fes_no":9,
    "uri_part": "1059"
  }
]

def _get_splatoon_ranking(fes_uri_part):
    r = requests.get(
        SPLATOON2_FESTIVAL_MATCH_RANKING_URI.format(fes_uri_part),
        cookies=COOKIES)
    if r.status_code == 403 and r.json().get('code') == AUTHENTICATION_ERROR:
        print("error: authentication error. make sure your iksm_session.")
        sys.exit(1)
    return r.text


def _make_ranking_json(json_file, fes_uri_part):
    try:
        with open(json_file, 'w') as f:
            f.write(_get_splatoon_ranking(fes_uri_part))
        print('processed:{}'.format(json_file))
    except:
        print("error: unexpected error is occured when writing json file.")


def _retrieve_ranking(fes_no=None):
    for fes in progressbar.progressbar(FES_URI_MAP, redirect_stdout=True):
        fes_no = fes['fes_no']
        fes_uri_part = fes['uri_part']
        # if json file already exists, skip processing
        json_file = '{}.json'.format(fes_no)
        if os.path.isfile(json_file):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if 'code' in data and (data['code'] == "INTERNAL_SERVER_ERROR" or data['code'] == "NOT_FOUND_ERROR"):
                        print("error: {}, fes_no:{}".format(data['code'],fes_no))
                        sys.exit(1)
                    else:
                        print('skipped: {}'.format(json_file))
                        continue
            except json.JSONDecodeError as e:
                print('JSONDecodeError: ', e)
                sys.exit(1)
        else:
            _make_ranking_json(json_file, fes_uri_part)
        sleep_delay = random.randrange(MIN_SLEEP_SEC, MAX_SLEEP_SEC)
        time.sleep(sleep_delay)


if __name__ == '__main__':
    if os.getenv("IKSM_SESSION"):
        IKSM_SESSION = os.getenv("IKSM_SESSION")
        COOKIES = dict(iksm_session=IKSM_SESSION)
    else:
        print("error: environment variable of IKSM_SESSION is required")
        sys.exit(1)

    _retrieve_ranking()
