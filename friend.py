import sqlite3
from flask import Flask, render_template, request, redirect, session
from datetime import datetime

app = Flask(__name__)


# フレンドリスト表示
def friend_index():
    if request.method == 'GET':
        conn = sqlite3.connect("thank.db")
        cur = conn.cursor()

        # ログイン中のユーザーのフレンドの名前を取得する
        cur.execute("SELECT * FROM users WHERE id IN (SELECT partner_id FROM friends WHERE user_id = ?)", (session["id"],))
        friends_information = cur.fetchall()

        conn.close()
        return render_template('friend_list.html', friends_information = friends_information)


# フレンド検索
def search():
    if request.method == 'GET':
        return render_template("friend_search.html")

    # リクエストがPOSTの時(検索フォームが入力された時)検索結果を表示する
    else:
        conn = sqlite3.connect("thank.db")
        cur = conn.cursor()

        # フォームに入力された名前と一致するユーザー名をusersテーブルから取得
        cur.execute("SELECT name FROM users WHERE name = ?", (request.form.get("search"),))
        searched_friend_name = cur.fetchall()
        
        conn.close()
        return render_template('friend_search.html', searched_friend_name = searched_friend_name)


# 友人追加の処理(friend.js経由でルーティング)
def add():
    conn = sqlite3.connect("thank.db")
    cur = conn.cursor()

    # 友人検索で選択された友人の名前をfirend_search.jsから受け取る
    added_friend_name = request.get_json()

    # 最初に、名前からSELECTして追加するパートナーのidを取得する
    cur.execute("SELECT id FROM users WHERE name = ?", (added_friend_name,))
    added_partner_id = cur.fetchall()[0][0]

    # friendsテーブルに、自分のuser_id, 追加するパートナーのuser_idを格納
    cur.execute("INSERT INTO friends (user_id, partner_id) VALUES (?, ?);",
            (session["id"], added_partner_id))
    conn.commit()

    conn.close()
    return redirect("/friend")


#フレンド削除
def delete():
    conn = sqlite3.connect("thank.db")
    cur = conn.cursor()

    if request.method == 'GET':
        # ログイン中のユーザーのフレンド情報を取得
        cur.execute("SELECT name FROM users WHERE id IN (SELECT partner_id FROM friends WHERE user_id = ?)", (session["id"],))
        friends_name = cur.fetchall()

        conn.close()
        return render_template("friend_delete.html", friends_name = friends_name)

    else:
        # 選択された友人の名前をfirend_delete.jsから受け取る
        deleted_friend_name = request.get_json()

        # 名前からSELECTして削除する人のidを取得する
        cur.execute("SELECT id FROM users WHERE name = ?", (deleted_friend_name,))
        deleted_partner_id = cur.fetchall()[0][0]

        # friendsテーブルから友人情報を削除する(user_idとpartner_idが一致するもの)
        cur.execute("DELETE FROM friends WHERE user_id = ? AND partner_id = ?", (session["id"], deleted_partner_id))
        conn.commit()

        conn.close()
        return redirect("/friend")
