from flask import Flask
from flask import render_template, request, redirect, session
# from flask_sqlalchemy import SQLAlchemy #SQLAlchemyを利用する
from datetime import datetime #時間取得のインポート
import pytz #時間の時差を計算
import sqlite3
from flask_session import Session

import datetime



app = Flask(__name__)
Session(app)

conn = sqlite3.connect("thank.db", check_same_thread=False)


# フレンドリスト表示機能
def friend_index():
    if request.method == 'GET':

        db = conn.cursor()

        # ログイン中のユーザーのフレンドの名前を取得する
        db.execute("SELECT * FROM users WHERE id IN (SELECT partner_id FROM friends WHERE user_id = ?)", (session["id"],))
        friends_information = db.fetchall()

        # フレンドリストを表示
        return render_template('friend_list.html', friends_information = friends_information)


# フレンド検索機能
def search():
    if request.method == 'GET':
        return render_template("friend_search.html")

    # POST(検索フォームが入力された時)検索結果を表示する
    else:

        db = conn.cursor()

        # フォームに名前を入力してもらい、一致する名前をusersテーブルから取得
        db.execute("SELECT name FROM users WHERE name = ?", (request.form.get("search"),))
        searched_friend_name = db.fetchall()
        print("aaa", searched_friend_name, request.form.get("search"))
        
        return render_template('friend_search.html', searched_friend_name = searched_friend_name) # 検索結果を表示する



# 友人追加を押した時の処理(friend.js経由でルーティング)
def add():

    db = conn.cursor()

    # 友人検索で選択された友人の名前をfirend_search.jsから受け取る
    added_friend_name = request.get_json()

    # 最初に、名前からSELECTして追加する人のidを取得する
    db.execute("SELECT id FROM users WHERE name = ?", (added_friend_name,))

    added_id = db.fetchall()[0][0]

    print("追加", added_id)
    print(session["id"])

    # friendsテーブルに、自分のuser_id, 追加する友人のuser_id, 時間をINSERTする
    db.execute("INSERT INTO friends (user_id, partner_id) VALUES (?, ?);",
            (session["id"], added_id))

    conn.commit()

    # フレンドリストの画面に戻る
    return redirect("/friend")


#フレンド削除用↓
def delete():

    db = conn.cursor()

    if request.method == 'GET':

        # ログイン中のユーザーのフレンド情報を取得
        db.execute("SELECT name FROM users WHERE id IN (SELECT partner_id FROM friends WHERE user_id = ?)", (session["id"],))
        
        # フレンドが登録されていない場合、データは存在しない
        try:
            friends_name = db.fetchall()
        except IndexError:
            friends_name = db.fetchall()

        # フレンド削除画面に移動
        return render_template("friend_delete.html", friends_name = friends_name)

    else:
        # 削除された友人の名前をfirend_delete.jsから受け取る
        deleted_friend_name = request.get_json()

        # 名前からSELECTして削除する人のidを取得する
        db.execute("SELECT id FROM users WHERE name = ?", (deleted_friend_name,))
        deleted_id = db.fetchall()[0][0]

        print("削除", deleted_id)

        # friendsテーブルから友人情報を削除する(user_idとpartner_idが一致するもの)
        db.execute("DELETE FROM friends WHERE user_id = ? AND partner_id = ?", (session["id"], deleted_id))
        conn.commit()

        # フレンドリストの画面に戻る
        return redirect("/friend")

