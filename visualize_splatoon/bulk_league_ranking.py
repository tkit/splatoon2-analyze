"""
Splatoon2のリーグマッチランキングをElasticsearchにbulkするpythonスクリプト
stage_listとleague_rankingのjsonファイルが期待した場所に置かれていること

elasticsearchは本スクリプトを動かすサーバと同一であること(localhost:9200)を期待する

usage: python bulk_league_ranking.py
"""

import json
import sys
import progressbar
from pathlib import Path
from datetime import datetime, timezone, timedelta
from elasticsearch import Elasticsearch, helpers, ElasticsearchException

ELASTICSEARCH_URL = "localhost:9200"
LEAGUE_RANKING_DIR = "../collect_splatoon_data/results"
LEAGUE_RANKING_FILE_PATTERN = "league_ranking_*.json"

es = Elasticsearch(ELASTICSEARCH_URL)
STAGE_LIST_JSON = "../collect_splatoon_data/results/stage_history.json"
JST = timezone(timedelta(hours=+9), 'JST')

MAX_BULK_FILE_COUNT = 1000


def _bulk_es_data(es, actions):
    try:
        helpers.bulk(es, actions)
    except ElasticsearchException as e:
        print('ElasticsearchException', e)
        print('elasticsearch url: {}'.format(ELASTICSEARCH_URL))
        sys.exit(1)


def _load_league_stage_list(f):
    with open(STAGE_LIST_JSON, 'r') as f:
        data = json.load(f)
    return data


def _convert_stage_dict(list):
    stage_dict = {}
    for l in list:
        if 'mode' in l and l['mode'] == "リーグマッチ":
            start_timestamp = int(l['start_time'])
            stage_dict[str(start_timestamp)] = {
                "rule": l['rule'], "stages": l['stages']}
        else:
            continue
    return stage_dict


def _load_league_ranking_file(json_file):
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print('JSONDecodeError: ', e)
        print('filename: {}'.format(json_file))
        return None


def _make_bulk_data(stage_info, ranking_data, start_time, league_type):
    dt = datetime.fromtimestamp(int(start_time), JST)
    actions = [{
        "_index":
            "splatoon_league_ranking",
        "_type":
            "league_ranking_history",
        "_id":
            '{}_{}_{}'.format(start_time, league_type, d['rank']),
        "league_ranking_region":
            "JP",
        "start_time":
            dt,
        "league_type":
            league_type,
        "rule":
            stage_info['rule'],
        "stages":
            stage_info['stages'],
        "rank":
            d['rank'],
        "point":
            d['point'],
        "tag_members": [{
            "main_weapon": t['weapon']['name'],
            "sub_weapon": t['weapon']['sub']['name'],
            "special_weapon": t['weapon']['special']['name']
        } for t in d['tag_members']]
    } for d in ranking_data]
    return actions


if __name__ == '__main__':
    stage_list = _load_league_stage_list(STAGE_LIST_JSON)
    stage_dict = _convert_stage_dict(stage_list)
    actions = []
    p = Path(LEAGUE_RANKING_DIR)
    file_count = len(list(p.glob(LEAGUE_RANKING_FILE_PATTERN)))
    for index, json_file in progressbar.progressbar(
            enumerate(list(p.glob(LEAGUE_RANKING_FILE_PATTERN))), redirect_stdout=True):
        data = _load_league_ranking_file(json_file)
        if "code" in data and data['code'] == "NOT_FOUND_ERROR":
            continue
        if "start_time" not in data:
            print("skipped because start_time isn't contained: {}".format(json_file))
            continue
        start_time = str(data['start_time'])
        if 'league_type' not in data or 'key' not in data['league_type']:
            print("skipped because league_type.key isn't contained: {}".format(json_file))
            continue
        league_type = data['league_type']['key']
        if start_time not in stage_dict:
            print('skipped because stage information is absent: {}'.format(
                datetime.fromtimestamp(int(start_time), JST)))
            continue

        actions.extend(
            _make_bulk_data(stage_dict[start_time], data['rankings'], start_time, league_type))
        if (index != 0 and index % MAX_BULK_FILE_COUNT == 0) or file_count == index:
            _bulk_es_data(es, actions)
            actions = []  # initialize
