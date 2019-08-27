# train ssについて

train_ss.pyは列車の運行状況を取得して、最新情報をslackにwebhookを使用して通知を行う為のプログラムです。

Python言語で開発されており、動作にはslackweb, requestsモジュールが必要です。

## 実行方法

train_ss.pyを動かすには、以下の環境変数が必要です。

- **SLACK_WEBHOOK**
 - slackのwebhook-URL
- **DATABASE_PATH**
 - 取得した情報を一時的に保存しておくSQLite3のファイル保存パス。初回起動時に自動生成されます。
- **TRAIN_SS_URLS**
 - データ取得元のURLが記載されたテキストファイル

```
# 実行方法の例（/tmpに必要なファイルが存在している場合）

pushd /tmp
export SLACK_WEBHOOK=https://hooks.slack.com/services/xxxxxxxxx/yyyyyyyyy/zzzzzzzzzzzzzzzzzzzzzzzz
export DATABASE_PATH=train_ss.db
export TRAIN_SS_URLS=train_ss.urls
python train_ss.py
popd
```

## 路線の追加方法

路線はtrain_ss.urlsに追記する事で行います。（１行１路線）

```
https://www.navitime.co.jp/train/00000141/ＪＲ山手線?nodeId=00004254
https://www.navitime.co.jp/train/00000797/りんかい線?nodeId=00005613
```
