# -*- coding: utf-8 -*-
"""
    実行には以下の環境変数が必要です。
    標準外のモジュールとして requests, slackweb を必要とします。

    SLACK_WEBHOOK
        slackのwebhook-URL
    DATABASE_PATH
        取得した情報を一時的に保存しておくSQLite3のファイル保存パス
    TRAIN_SS_URLS
        データ取得元のURLが記載されたテキストファイル
"""
import sys
import os
import re
import hashlib
import datetime
import sqlite3

import requests
import slackweb

RE_PATTERN_NONE = ("<div class=\"RailInfoTextOperation_none\">(.*?)</div>")
RE_PATTERN_TEXT = (
    "<div class=\"RailInfoTextOperation\">.*"
    "<div>(.*?)<span class=\"RailInfoTextOperationInfo.*?\">(.*?)</span>.*</div>.*"
    "<div class=\"RailInfoTextText\">(.*?)</div>.*"
    "<div class=\"RailInfoTextTime\">(.*?)</div>")


def update_train_status(url, text):
    """

    Args:
        url (text):
        text (text):

    Returns:
        前回と異なるテキストが与えられた場合はTrueを戻します。
    """

    ins_hash = hashlib.sha1(text.encode("utf-8")).hexdigest()
    ins_date = datetime.datetime.now()

    r_count = 0
    changed = True

    o_conn = sqlite3.connect(os.environ.get("DATABASE_PATH"))
    o_conn.execute("""
        CREATE TABLE IF NOT EXISTS last_status(
            url varchar(250) PRIMARY KEY
        ,   sha1hash varchar(128)
        ,   last_update varchar(64)
        )
        """)

    result = o_conn.execute(
        "SELECT url, sha1hash FROM last_status WHERE url = ?", (url, ))

    for r in result:
        r_count += 1
        if r[1] == ins_hash:
            changed = False
            break

    if r_count == 0:
        o_conn.execute(
            "INSERT INTO last_status (url, sha1hash, last_update) VALUES(?, ?, ?)",
            (url, ins_hash, ins_date))
        o_conn.commit()
        changed = True
    elif changed is True:
        o_conn.execute(
            "UPDATE last_status SET sha1hash = ?, last_update = ? WHERE url = ?",
            (ins_hash, ins_date, url))
        o_conn.commit()

    return changed


def route_check(url):
    """
    """

    route_name = re.search("/train/[0-9]+/(.*?)\?", url).group(1)

    o_req = requests.get(url)
    raw_html = o_req.text

    try:
        o_search = re.search(RE_PATTERN_NONE, raw_html.replace("&nbsp;", " "),
                             re.MULTILINE | re.DOTALL)
        combined_text = u"*{0}:* {1}\n>>>{2}".format(route_name,
                                                     o_search.group(1), url)
    except AttributeError:
        o_search = re.search(RE_PATTERN_TEXT, raw_html.replace("&nbsp;", " "),
                             re.MULTILINE | re.DOTALL)
        combined_text = u"*{0}:* {1}\n>>>{2}\n{3}\n{4}".format(
            route_name, o_search.group(2), o_search.group(3),
            o_search.group(4), url)

    if update_train_status(url, combined_text) is True:
        o_slack = slackweb.Slack(os.environ.get("SLACK_WEBHOOK"))
        o_slack.notify(text=combined_text)


def main():
    """
    """

    for k in ("SLACK_WEBHOOK", "DATABASE_PATH", "TRAIN_SS_URLS"):
        if os.environ.get(k, "") == "":
            print("The environment variable '{0}' is not set. ".format(k))
            return 1

    with open(os.environ.get("TRAIN_SS_URLS"), "r") as h_reader:
        for url in h_reader.readlines():
            route_check(url.decode("utf-8").strip())

    return 0


if __name__ == "__main__":
    sys.exit(main())
