"""
Splatoon2のスケジュールを取得し、jsonファイルで保存するスクリプト

環境変数IKSM_SESSIONに各自のiksm_sessionを設定しておく必要あり

usage: python get_schedule.py
"""

import json
import sys
from pathlib import Path
from splatoon import SplatoonClient
from splatoon_exceptions import AuthenticationError, ValueError

OUTPUT_DIR = 'results'
OUTPUT_FILE_FORMAT = 'schedule_{}.json'


def _make_stage_history_map(schedules):
    formatted_schedule = [{
        "start_time": int(i["start_time"]),
        "mode": i["game_mode"]["name"],
        "rule": i["rule"]["name"],
        "stages": [{
            "name": i[k]["name"]
        } for k in list(i.keys()) if k.startswith('stage_')]
    } for j in list(schedules.values()) for i in j]
    return formatted_schedule


def _save_json(schedule):
    p = Path(OUTPUT_DIR)
    if not p.exists() or not p.is_dir():
        p.mkdir()
    for stages in schedule:
        output_file = '{}/{}'.format(OUTPUT_DIR,
                                     OUTPUT_FILE_FORMAT.format(stages["start_time"]))
        pf = Path(output_file)
        if pf.exists() and pf.is_file():
            try:
                with open(output_file, 'r+') as f:
                    stage_history = json.load(f)
                    if stages in stage_history:
                        print("skipped: stage {} already exists in {}".format(
                            stages, output_file))
                    else:
                        print("updated: stage {} added to {}".format(
                            stages, output_file))
                        stage_history.append(stages)
                        f.seek(0)
                        f.write(json.dumps(stage_history, indent=4))
            except json.JSONDecodeError as e:
                print('JSONDecodeError: ', e)
                print('filename: {}'.format(output_file))
                return None
        else:
            with open(output_file, 'w') as f:
                print("created: stage {} saved to {}".format(stages, output_file))
                f.write(json.dumps([stages], indent=4))


if __name__ == '__main__':
    try:
        sc = SplatoonClient()
    except ValueError as e:
        print(e)
        sys.exit(1)
    try:
        schedules = sc.get_schedules()
    except AuthenticationError as e:
        print(e)
        sys.exit(1)

    formatted_schedule = _make_stage_history_map(schedules)
    _save_json(formatted_schedule)
