"""
Splatoon2のフェスマッチランキングの結果を取得し、jsonファイルで保存するスクリプト
初回から全ての結果を取得する(既に取得済みのものは再取得しない)

環境変数IKSM_SESSIONに各自のiksm_sessionを設定しておく必要あり

usage: python get_festival_ranking.py
"""

import json
import time
import random
import progressbar
import sys
from pathlib import Path
from splatoon import SplatoonClient
from splatoon_exceptions import AuthenticationError, ValueError

MIN_SLEEP_SEC = 2
MAX_SLEEP_SEC = 5
OUTPUT_DIR = 'results'
OUTPUT_FILE_FORMAT = 'festival_ranking_{}.json'


def _make_ranking_json(sc, output_file, fes_uri_part):
    try:
        with open(output_file, 'w') as f:
            f.write(sc.get_festival_ranking(fes_uri_part))
        print('processed:{}'.format(output_file))
    except AuthenticationError as e:
        print(e)
        sys.exit(1)
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


def _retrieve_ranking(sc, festival_history):
    p = Path(OUTPUT_DIR)
    if not p.exists() or not p.is_dir():
        p.mkdir()
    for fes in progressbar.progressbar(festival_history, redirect_stdout=True):
        fes_uri_part = fes['festival_id']
        # if json file already exists, skip processing
        output_file = '{}/{}'.format(OUTPUT_DIR,
                                     OUTPUT_FILE_FORMAT.format(fes['end_time']))
        pf = Path(output_file)
        if pf.exists() and pf.is_file():
            try:
                with open(output_file, 'r') as f:
                    data = json.load(f)
                    if 'code' in data and (data['code'] == "INTERNAL_SERVER_ERROR" or
                                           data['code'] == "NOT_FOUND_ERROR"):
                        print("error: {}, fes_end_time:{}".format(
                            data['code'], fes['end_time']))
                        sys.exit(1)
                    else:
                        print('skipped: {}'.format(output_file))
                        continue
            except json.JSONDecodeError as e:
                print('JSONDecodeError: ', e)
                sys.exit(1)
        else:
            _make_ranking_json(sc, output_file, fes_uri_part)
        sleep_delay = random.randrange(MIN_SLEEP_SEC, MAX_SLEEP_SEC)
        time.sleep(sleep_delay)


if __name__ == '__main__':
    try:
        sc = SplatoonClient()
    except ValueError as e:
        print(e)
        sys.exit(1)
    try:
        festival_history = sc.get_festival_list()
    except AuthenticationError as e:
        print(e)
        sys.exit(1)

    festival_map = _make_festival_map(festival_history)

    _retrieve_ranking(sc, festival_map)
