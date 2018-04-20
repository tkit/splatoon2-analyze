festival_ranking
====

splatoon2のapiにアクセスし、過去のフェスマッチのランキング結果を取得し、json形式で保存します。

# how to setup

```
pip install -r requirements.txt
```

# how to run

```
export IKSM_SESSION=<your_iksm_session>
python get_festival_ranking.py
```

結果は同ディレクトリ内に `<festival_no>.json` という形で保存されます。  

# caution

* 高負荷アクセスを防ぐため、sleepが入っています。約6000件(約7ヶ月分)の取得で6hほどかかります。

# another way (use Docker)

## build

```
docker build -t splatoon_festival_ranking .
```

## run

```
docker run --rm --name festival_ranking -e IKSM_SESSION=<your_iksm_session> -v $PWD:/app splatoon_festival_ranking:latest
```

