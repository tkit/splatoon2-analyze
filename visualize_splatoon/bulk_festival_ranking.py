"""
Splatoon2のフェスマッチランキングをElasticsearchにbulkするpythonスクリプト
festival_rankingのjsonファイルが期待した場所に置かれていること

elasticsearchは本スクリプトを動かすサーバと同一であること(localhost:9200)を期待する

usage: python bulk_festival_ranking.py
"""

import json
import sys
import progressbar
from pathlib import Path
from datetime import datetime, timezone, timedelta
from elasticsearch import Elasticsearch, helpers, ElasticsearchException

ELASTICSEARCH_URL = "localhost:9200"
FESTIVAL_RANKING_DIR = "../festival_ranking"
FESTIVAL_RANKING_FILE_PATTERN = "*.json"

es = Elasticsearch(ELASTICSEARCH_URL)
JST = timezone(timedelta(hours=+9), 'JST')


def _bulk_es_data(es, actions):
    try:
        helpers.bulk(es, actions)
    except ElasticsearchException as e:
        print('ElasticsearchException', e)
        print('elasticsearch url: {}'.format(ELASTICSEARCH_URL))
        sys.exit(1)


def _load_festival_ranking_file(jeson_file):
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print('JSONDecodeError: ', e)
        print('filename: {}'.format(json_file))
        return None


def _make_bulk_data(ranking_data, end_time):
    actions = []
    for team in ["alpha", "bravo"]:
        actions.extend([{
            "_index":
                "splatoon_festival_ranking",
            "_type":
                "festival_ranking_history",
            "_id":
                '{}_{}_{}'.format(end_time, team, d['order']),
            "team":
                team,
            "end_time":
                end_time,
            "name":
                d['info']['nickname'],
            "score":
                d['score'],
            "order":
                d['order'],
            "weapon": {
                "main_weapon": d['info']['weapon']['name'],
                "sub_weapon": d['info']['weapon']['sub']['name'],
                "special_weapon": d['info']['weapon']['special']['name']
            },
            "gear": [{
                "part":
                    d['info']['head']['kind'],
                "frequent_skill":
                    d['info']['head']['brand']['frequent_skill']['name']
                    if 'frequent_skill' in d['info']['head']['brand'] else 'なし',
                "brand":
                    d['info']['head']['brand']['name']
            }, {
                "part":
                    d['info']['clothes']['kind'],
                "frequent_skill":
                    d['info']['clothes']['brand']['frequent_skill']['name']
                    if 'frequent_skill' in d['info']['clothes']['brand'] else 'なし',
                "brand":
                    d['info']['clothes']['brand']['name']
            }, {
                "part":
                    d['info']['shoes']['kind'],
                "frequent_skill":
                    d['info']['shoes']['brand']['frequent_skill']['name']
                    if 'frequent_skill' in d['info']['shoes']['brand'] else 'なし',
                "brand":
                    d['info']['shoes']['brand']['name']
            }]
        } for d in ranking_data[team]])
    return actions


if __name__ == '__main__':
    p = Path(FESTIVAL_RANKING_DIR)
    actions = []
    for json_file in progressbar.progressbar(
            list(p.glob(FESTIVAL_RANKING_FILE_PATTERN)), redirect_stdout=True):
        data = _load_festival_ranking_file(json_file)
        if not "rankings" in data and not "alpha" in data['rankings'] and not isinstance(
                data['rankings']['alpha'],
                list) and not "updated_time" in data['rankings']['alpha'][0]:
            print("skipped because this data isn't formatted structure: {}".format(json_file))
            continue
        end_time = int(str(json_file.name).split(".")[0])
        end_time = datetime.fromtimestamp(int(end_time), JST)
        actions = _make_bulk_data(data['rankings'], end_time)
        _bulk_es_data(es, actions)
