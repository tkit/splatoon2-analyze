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
from pathlib import Path
import splatoon
from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=+9), 'JST')
DEFAULT_COUNT_DAYS_AGO = 3
FIRST_TIME_OF_LEAGUE_MATCH = datetime(
    year=2017, month=7, day=21, hour=10, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

MIN_SLEEP_SEC = 2
MAX_SLEEP_SEC = 5
AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR'
OUTPUT_DIR = 'results'
OUTPUT_FILE_FORMAT = 'league_ranking_{}.json'


def _make_ranking_json(sc, output_file, uri_time):
    try:
        with open(output_file, 'w') as f:
            f.write(sc.get_league_ranking(uri_time))
        print('processed:{}'.format(output_file))
    except:
        print("error: unexpected error is occured when writing json file.")


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


def _retrieve_ranking(sc, ranking_date_list):
    p = Path(OUTPUT_DIR)
    if not p.exists() or not p.is_dir():
        p.mkdir()
    for uri_time in progressbar.progressbar(ranking_date_list, redirect_stdout=True):
        # if json file already exists, skip processing
        output_file = '{}/{}'.format(OUTPUT_DIR,OUTPUT_FILE_FORMAT.format(uri_time))
        pf = Path(output_file)
        if pf.exists() and pf.is_file():
            try:
                with open(output_file, 'r') as f:
                    data = json.load(f)
                    if 'code' in data and data['code'] == "NOT_FOUND_ERROR":
                        _make_ranking_json(sc, output_file, uri_time)
                    else:
                        print('skipped:{}'.format(output_file))
                        continue
            except json.JSONDecodeError as e:
                print('JSONDecodeError: ', e)
        else:
            _make_ranking_json(sc, output_file, uri_time)
        sleep_delay = random.randrange(MIN_SLEEP_SEC, MAX_SLEEP_SEC)
        time.sleep(sleep_delay)


if __name__ == '__main__':
    if os.getenv("IKSM_SESSION"):
        iksm_session = os.getenv("IKSM_SESSION")
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

    sc = splatoon.SplatoonClient(iksm_session)
    ranking_date_list = _get_ranking_date_list()
    _retrieve_ranking(sc, ranking_date_list)
