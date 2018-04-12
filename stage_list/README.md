stage_list
====

splatoon2の過去のルール/ステージ一覧を整形してjson形式で保存します。

前提として[TwimeMachine](http://www.twimemachine.com/)サービスを利用して[@splatoon2_stage](https://twitter.com/splatoon2_stage)のtweet結果をローカルに保管している必要があります。

# how to setup

```
pip install -r requirements.txt
```

# how to run

```
python get_stage_list.py <source_file>
```

`source_file` にはTwimeMachineから保存したHTMLのソースを指定します。

結果は同ディレクトリ内に `stage_list.json` という形で保存されます。
