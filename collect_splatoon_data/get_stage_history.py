"""
Splatoon2のステージリストを生成しjsonファイルで保存するpythonスクリプト
結果はstage_history.jsonとして出力される

引数にソースファイル(Twimemachineから取得したHTML)が必要
http://www.twimemachine.com/user/splatoon2_stage/

usage: python get_stage_history.py <source_file_name>
"""

import re
import json
import os
import sys
import progressbar
from pathlib import Path
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

JST = timezone(timedelta(hours=+9), 'JST')
OUTPUT_DIR = 'results'
OUTPUT_FILE = 'stage_history.json'


class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.tweetbody = False
        self.tweetdate = None
        self.data = []

    def handle_starttag(self, tag, attrs):
        if tag == "span":
            self.tweetbody = True
            for attr in attrs:
                if attr[0] == 'rel':
                    tweetdate = attr[1]
                    dt = datetime.strptime(tweetdate, "%a %b %d %H:%M:%S %z %Y")
                    self.tweetdate = dt.astimezone(tz=JST)

    def handle_data(self, data):
        if self.tweetbody:
            self.data.append({"data": data, "tweetdate": self.tweetdate})
            self.tweetbody = False
            self.tweetdate = None


def _html_parse(source_file):
    parser = MyHTMLParser()
    with open(source_file, encoding='utf-8') as f:
        parser.feed(f.read())
    return parser.data


def _get_match_date(pattern, data):
    match_date = pattern.search(data['data'])
    if match_date:
        dt = datetime.strptime('{}'.format(match_date.group()), "%m/%d %H:%M")
        dt = dt.replace(tzinfo=JST)
        dt = dt.replace(year=data['tweetdate'].year)
        return dt
    return None


def _make_match_dict(match_detail, match_date):
    stage_dict = {
        "start_time": match_date.timestamp(),
        "mode": match_detail['mode'],
        "rule": match_detail['rule'],
        "stages": match_detail['stages']
    }
    return stage_dict


def _get_nawabari_history(pattern, search_string):
    match = pattern.search(search_string)
    if match:
        stages = [{"name": s} for s in match.group(1).split("、")]
        return {"mode": "レギュラーマッチ", "rule": "ナワバリバトル", "stages": stages}


def _get_gachi_history(pattern, search_string):
    match = pattern.search(search_string)
    if match:
        rule = _normalize_rule(match.group(1))
        stages = [{"name": s} for s in match.group(2).split("、")]
        return {"mode": "ガチマッチ", "rule": rule, "stages": stages}
    return None


def _get_league_history(pattern, search_string):
    match = pattern.search(search_string)
    if match:
        rule = _normalize_rule(match.group(1))
        stages = [{"name": s} for s in match.group(2).split("、")]
        return {"mode": "リーグマッチ", "rule": rule, "stages": stages}
    return None


def _get_fes_history(pattern, search_string):
    match = pattern.search(search_string)
    if match:
        stages = [{"name": m} for m in list(match.group(1, 2, 3))]
        return {"mode": "フェスマッチ", "rule": "ナワバリ", "stages": stages}
    return None


def _normalize_rule(rule):
    """
  「ガチホコ」と「ガチホコバトル」で表記ゆれがあるため、「ガチホコバトル」に統一
  """
    if rule == 'ガチホコ':
        return 'ガチホコバトル'
    return rule


def _make_stage_history(source_file):
    parsed_data = _html_parse(source_file)

    regex_date = r'\d{2}/\d{2}\s\d{2}:\d{2}'
    pattern_date = re.compile(regex_date)

    regex_nawabari = r'^▼ナワバリ\n(.*)$'
    pattern_nawabari = re.compile(regex_nawabari, re.MULTILINE)

    regex_gachi = r'^▼(ガチ.*)\n(.*)$'
    pattern_gachi = re.compile(regex_gachi, re.MULTILINE)

    regex_league = r'^▼リーグ：(\w+)\n(\S+)'
    pattern_league = re.compile(regex_league, re.MULTILINE)

    regex_fes = r'▼フェスマッチ\n(\S+)\n(\S+)\n(\S+)'
    pattern_fes = re.compile(regex_fes, re.MULTILINE)

    stage_history = []

    for i in progressbar.progressbar(parsed_data, redirect_stdout=True):
        match_date = _get_match_date(pattern_date, i)
        if not match_date:
            continue
        match = _get_nawabari_history(pattern_nawabari, i['data'])
        if match:
            stage_history.append(_make_match_dict(match, match_date))
        match = _get_gachi_history(pattern_gachi, i['data'])
        if match:
            stage_history.append(_make_match_dict(match, match_date))
        match = _get_league_history(pattern_league, i['data'])
        if match:
            stage_history.append(_make_match_dict(match, match_date))
        match = _get_fes_history(pattern_fes, i['data'])
        if match:
            stage_history.append(_make_match_dict(match, match_date))

    return stage_history


def _save_json(stage_history):
    p = Path(OUTPUT_DIR)
    if not p.exists() or not p.is_dir():
        p.mkdir()
    output_file = '{}/{}'.format(OUTPUT_DIR, OUTPUT_FILE)
    with open(output_file, 'w') as f:
        f.write(json.dumps(stage_history, indent=4))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("error: source file is required")
        sys.exit(1)
    source_file = sys.argv[1]
    if os.path.isfile(source_file) == False:
        print("error: source file is not found: {}".format(source_file))
        sys.exit(1)

    stage_history = _make_stage_history(source_file)
    _save_json(stage_history)
