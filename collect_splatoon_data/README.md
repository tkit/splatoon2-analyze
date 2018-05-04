collect_splatoon_data
festival_ranking
====

splatoon2のapiにアクセスし、様々なデータを取得します。

* `festival_ranking`: 過去のフェスマッチのランキング結果を取得し、json形式で保存します。
* `league_ranking`: 過去のリーグマッチのランキング結果を取得し、json形式で保存します。
* `stage_history`: splatoon2の過去のルール/ステージ一覧を整形してjson形式で保存します。
* `schedule`: splatoon2の現在(から24時間先まで)のルール/ステージ一覧を整形してjson形式で保存します。

# how to setup (common)

```
pip install pipenv
pipenv install
pipenv install --dev # for development
```

# how to run

## festival_ranking

```
export IKSM_SESSION=<your_iksm_session>
pipenv run sp_festival
```

結果は`results`ディレクトリ内に `festival_ranking_<timestamp>.json` という形で保存されます。  

## league_ranking

```
export IKSM_SESSION=<your_iksm_session>
pipenv run sp_league <days>
```

`days` には何日前(から現在まで)の結果を取得するかを指定します。指定しない場合はデフォルトの「3日前」が選択されます。

結果は`results`ディレクトリ内に `YYMMDDHHT.json` または `YYMMDDHHP.json` という形で保存されます。  
日時はUTCであることにご注意ください。  

`T` または `P` は以下の意味を持ちます。

* `T` : Team(4人戦)
* `P` : Pair(2人戦)

### caution

* 高負荷アクセスを防ぐため、sleepが入っています。約6000件(約7ヶ月分)の取得で6hほどかかります。
* リージョンは日本地域のみです。(マッピングするステージ情報がおそらく日本地域のみしか取得できないため)

## stage_history

```
pipenv run sp_stage <source_file>
```

`source_file` にはTwimeMachineから保存したHTMLのソースを指定します。

結果は`results`ディレクトリ内に `stage_list.json` という形で保存されます。

## schedule

```
pipenv run sp_schedule
```

結果は`results`ディレクトリ内に `schedule_<timestamp>.json` という形で保存されます。


# another way (use Docker)

## build

```
docker build -t collect_splatoon_data .
```

## run

```
docker run --rm --name collect_splatoon_data -e IKSM_SESSION=<your_iksm_session> -v $PWD:/app collect_splatoon_data:latest get_festival_ranking.py # festival_ranking
docker run --rm --name collect_splatoon_data -e IKSM_SESSION=<your_iksm_session> -v $PWD:/app collect_splatoon_data:latest get_league_ranking.py <days> # league_ranking
docker run --rm --name collect_splatoon_data -e IKSM_SESSION=<your_iksm_session> -v $PWD:/app collect_splatoon_data:latest get_stage_history.py <source_file> # stage_list
docker run --rm --name collect_splatoon_data -e IKSM_SESSION=<your_iksm_session> -v $PWD:/app collect_splatoon_data:latest get_schedule.py # schedule
```

