from flask import Flask
from flask import render_template, request, redirect, session
# from flask_sqlalchemy import SQLAlchemy #SQLAlchemyを利用する
from datetime import datetime #時間取得のインポート
import pytz #時間の時差を計算
from cs50 import SQL
from flask_session import Session

import datetime



app = Flask(__name__)
Session(app)

db = SQL("sqlite:///thank.db")


# フレンドリスト表示機能
def friend_index():
    if request.method == 'GET':

        # ログイン中のユーザーのフレンドの名前を取得する
        friends_information = db.execute("SELECT * FROM users WHERE id IN (SELECT partner_id FROM friends WHERE user_id = ?)", session["id"])

        # フレンドリストを表示
        return render_template('friend_list.html', friends_information = friends_information)


# フレンド検索機能
def search():
    if request.method == 'GET':
        return render_template("friend_search.html")

    # POST(検索フォームが入力された時)検索結果を表示する
    else:

        # フォームに名前を入力してもらい、一致する名前をusersテーブルから取得
        searched_friend_name = db.execute("SELECT name FROM users WHERE name = ?", request.form.get("search"))

        return render_template('friend_search.html', searched_friend_name = searched_friend_name) # 検索結果を表示する



# 友人追加を押した時の処理(friend.js経由でルーティング)
def add():

    # 友人検索で選択された友人の名前をfirend_search.jsから受け取る
    added_friend_name = request.get_json()

    # 最初に、名前からSELECTして追加する人のidを取得する
    added_id = db.execute("SELECT id FROM users WHERE name = ?", added_friend_name)[0]["id"]

    # friendsテーブルに、自分のuser_id, 追加する友人のuser_id, 時間をINSERTする
    db.execute("INSERT INTO friends (user_id, partner_id, created_at, updated_at) VALUES (?, ?, ?, ?)",
            session["id"], added_id, datetime.datetime.now(), datetime.datetime.now())

    # フレンドリストの画面に戻る
    return redirect("/friend")


#フレンド削除用↓
def delete():
    if request.method == 'GET':

        # ログイン中のユーザーのフレンド情報を取得
        friends_name = db.execute("SELECT name FROM users WHERE id IN (SELECT partner_id FROM friends WHERE user_id = ?)", session["id"])

        # フレンド削除画面に移動
        return render_template("friend_delete.html", friends_name = friends_name)

    else:
        # 削除された友人の名前をfirend_delete.jsから受け取る
        deleted_friend_name = request.get_json()

        # 名前からSELECTして削除する人のidを取得する
        deleted_id = db.execute("SELECT id FROM users WHERE name = ?", deleted_friend_name)[0]["id"]

        # friendsテーブルから友人情報を削除する(user_idとpartner_idが一致するもの)
        db.execute("DELETE FROM friends WHERE user_id = ? AND partner_id = ?", session["id"], deleted_id)

        # フレンドリストの画面に戻る
        return redirect("/friend")

