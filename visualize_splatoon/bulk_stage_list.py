import json
from datetime import datetime
from elasticsearch import Elasticsearch, helpers

ELASTICSEARCH_URL = "localhost:9200"

es = Elasticsearch(ELASTICSEARCH_URL)
JSON_FILE = "../stage_list/stage_history.json"


def _bulk_es(data):
    actions = [{
        "timestamp":
        datetime.strptime(d['start_time'], '%Y/%m/%d %H:%M %z'),
        "mode":
        d['mode'],
        "rule":
        d['rule'],
        "stages":
        d['stages'],
        "_index":
        "splatoon_stages",
        "_type":
        "stage_history",
        "_id":
        '{}_{}'.format(
            datetime.strptime(d['start_time'],
                              '%Y/%m/%d %H:%M %z').timestamp(), d['mode'])
    } for d in data]
    helpers.bulk(es, actions)


if __name__ == '__main__':
    with open(JSON_FILE, 'r') as f:
        data = json.load(f)
    _bulk_es(data)
