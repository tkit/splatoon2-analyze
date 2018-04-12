league_ranking
====

splatoon2のapiにアクセスし、過去のリーグマッチのランキング結果を取得し、json形式で保存します。

# how to setup

```
pip install -r requirements.txt
```

# how to run

```
export IKSM_SESSION=<your_iksm_session>
python get_league_ranking.py <days>
```

`days` には何日前(から現在まで)の結果を取得するかを指定します。指定しない場合はデフォルトの「3日前」が選択されます。

結果は同ディレクトリ内に `YYMMDDHHT.json` または `YYMMDDHHP.json` という形で保存されます。  
日時はUTCであることにご注意ください。  

`T` または `P` は以下の意味を持ちます。

* `T` : Team(4人戦)
* `P` : Pair(2人戦)

