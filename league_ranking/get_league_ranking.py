"""
Splatoon2のリーグマッチランキングの結果を取得し、jsonファイルで保存するスクリプト
引数で何日前からのデータを保管するかを指定可能
設定しない場合、デフォルトの日数前からの結果を取得する

環境変数IKSM_SESSIONに各自のiksm_sessionを設定しておく必要あり

usage: python get_league_ranking.py 2 # from 2 days ago to now
usage: python get_league_ranking.py # from 3 days ago(default) to now
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
DEFAULT_COUNT_DAYS_AGO = 3
SPLATOON2_LEAGUE_MATCH_RANKING_URI = 'https://app.splatoon2.nintendo.net/api/league_match_ranking/{}/ALL'
FIRST_TIME_OF_LEAGUE_MATCH = datetime(
    year=2017,
    month=7,
    day=21,
    hour=10,
    minute=0,
    second=0,
    microsecond=0,
    tzinfo=timezone.utc)

MIN_SLEEP_SEC = 2
MAX_SLEEP_SEC = 5


def _get_splatoon_ranking(match_date_uri):
    r = requests.get(
        SPLATOON2_LEAGUE_MATCH_RANKING_URI.format(match_date_uri),
        cookies=COOKIES)
    return r.text


def _make_ranking_json(json_file, uri_time):
    with open(json_file, 'w') as f:
        f.write(_get_splatoon_ranking(uri_time))
    print('processed:{}'.format(json_file))


def _get_ranking_date_list():
    match_time = start_time
    time_now = datetime.now(tz=timezone.utc)
    ranking_date_list = []
    while (match_time < time_now):
        uri_base_time = match_time.strftime('%y%m%d%H')
        ranking_date_list.append('{}P'.format(uri_base_time))
        ranking_date_list.append('{}T'.format(uri_base_time))
        match_time = match_time + timedelta(hours=2)  # 2 hours interval
    return ranking_date_list


def _retrieve_ranking(ranking_date_list):
    for uri_time in progressbar.progressbar(
            ranking_date_list, redirect_stdout=True):
        # if json file already exists, skip processing
        json_file = '{}.json'.format(uri_time)
        if os.path.isfile(json_file):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    if 'code' in data and data['code'] == "NOT_FOUND_ERROR":
                        _make_ranking_json(json_file, uri_time)
                    else:
                        print('skipped:{}'.format(json_file))
                        continue
            except json.JSONDecodeError as e:
                print('JSONDecodeError: ', e)
        else:
            _make_ranking_json(json_file, uri_time)
        sleep_delay = random.randrange(MIN_SLEEP_SEC, MAX_SLEEP_SEC)
        time.sleep(sleep_delay)


if __name__ == '__main__':
    if os.getenv("IKSM_SESSION"):
        IKSM_SESSION = os.getenv("IKSM_SESSION")
        COOKIES = dict(iksm_session=IKSM_SESSION)
    else:
        print("error: environment IKSM_SESSION is required")
        sys.exit(1)
    
    now = datetime.now(timezone.utc)
    
    if len(sys.argv) == 1:  # default
        start_time = (now - timedelta(days=DEFAULT_COUNT_DAYS_AGO)).replace(
            hour=0, minute=0, second=0, microsecond=0)
    elif len(sys.argv) > 2:
        print("error: param1 is required")
        sys.exit(1)
    elif sys.argv[1].isdigit() == False:
        print("error: param1 must be integer")
        sys.exit(1)
    elif int(sys.argv[1]) <= 0:
        print("error: param1 must be larger than 0")
        sys.exit(1)
    else:
        start_time = (now - timedelta(days=int(sys.argv[1]))).replace(
            hour=0, minute=0, second=0, microsecond=0)
    
    if FIRST_TIME_OF_LEAGUE_MATCH > start_time:
        start_time = FIRST_TIME_OF_LEAGUE_MATCH
    print('start time is {}'.format(start_time.strftime('%y%m%d%H')))

    ranking_date_list = _get_ranking_date_list()
    _retrieve_ranking(ranking_date_list)

