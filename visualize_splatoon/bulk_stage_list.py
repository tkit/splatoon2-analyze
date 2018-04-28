import json
import progressbar
from pathlib import Path
from datetime import datetime, timezone, timedelta
from elasticsearch import Elasticsearch, helpers

ELASTICSEARCH_URL = "localhost:9200"
STAGE_LIST_DIR = "../collect_splatoon_data/results"
STAGE_LIST_FILE_PATTERN = "stage_history.json"

es = Elasticsearch(ELASTICSEARCH_URL)
JST = timezone(timedelta(hours=+9), 'JST')


def _bulk_es(data):
    actions = [{
        "timestamp": datetime.fromtimestamp(int(d['start_time']), JST),
        "mode": d['mode'],
        "rule": d['rule'],
        "stages": d['stages'],
        "_index": "splatoon_stages",
        "_type": "stage_history",
        "_id": '{}_{}'.format(int(d['start_time']), d['mode'])
    } for d in data]
    helpers.bulk(es, actions)


def _load_stage_list_file(json_file):
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print('JSONDecodeError: ', e)
        print('filename: {}'.format(json_file))
        return None


if __name__ == '__main__':
    p = Path(STAGE_LIST_DIR)
    for json_file in progressbar.progressbar(
            list(p.glob(STAGE_LIST_FILE_PATTERN)), redirect_stdout=True):
        data = _load_stage_list_file(json_file)
        _bulk_es(data)
