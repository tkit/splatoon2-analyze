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
SPLATOON2_FESTIVAL_HISTORY_URI = 'https://app.splatoon2.nintendo.net/api/festivals/pasts'
MIN_SLEEP_SEC = 2
MAX_SLEEP_SEC = 5
AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR'

if os.getenv("IKSM_SESSION"):
    IKSM_SESSION = os.getenv("IKSM_SESSION")
    COOKIES = dict(iksm_session=IKSM_SESSION)
else:
    print("error: environment variable of IKSM_SESSION is required")
    sys.exit(1)


def _get_splatoon_ranking(fes_uri_part):
    return _get_splatoon_request(SPLATOON2_FESTIVAL_MATCH_RANKING_URI.format(fes_uri_part)).text


def _get_festival_list():
    return _get_splatoon_request(SPLATOON2_FESTIVAL_HISTORY_URI).json()


def _get_splatoon_request(url):
    r = requests.get(url, cookies=COOKIES)
    if r.status_code == 403 and r.json().get('code') == AUTHENTICATION_ERROR:
        print("error: authentication error. make sure your iksm_session.")
        sys.exit(1)
    return r


def _make_ranking_json(json_file, fes_uri_part):
    try:
        with open(json_file, 'w') as f:
            f.write(_get_splatoon_ranking(fes_uri_part))
        print('processed:{}'.format(json_file))
    except:
        print("error: unexpected error is occured when writing json file.")


def _make_festival_map(festival_history):
    fes_list = [{
        "festival_id": f['festival_id'],
        "end_time": f['times']['end'],
        "alpha": f['names']['alpha_long'],
        "bravo": f['names']['bravo_long']
    } for f in festival_history['festivals']]
    return fes_list


def _retrieve_ranking(festival_history):
    for fes in progressbar.progressbar(festival_history, redirect_stdout=True):
        fes_uri_part = fes['festival_id']
        # if json file already exists, skip processing
        json_file = '{}.json'.format(fes['end_time'])
        if os.path.isfile(json_file):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if 'code' in data and (data['code'] == "INTERNAL_SERVER_ERROR" or
                                           data['code'] == "NOT_FOUND_ERROR"):
                        print("error: {}, fes_end_time:{}".format(data['code'], fes['end_time']))
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
    festival_history = _get_festival_list()
    festival_map = _make_festival_map(festival_history)

    _retrieve_ranking(festival_map)
