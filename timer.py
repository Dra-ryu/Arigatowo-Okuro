import json
import os
import requests
import sys
import sqlite3

from flask import Flask, render_template, request, abort, redirect
from linebot import LineBotApi
from linebot.models import TextSendMessage
from flask_session import Session


db = sqlite3.connect("thank.db", check_same_thread=False)

app = Flask(__name__)

# 以下、LINE bot関連の情報

#  チャネルアクセストークンはhttps://developers.line.biz/console/channel/1656501143/messaging-apiから取得
LINE_CHANNEL_ACCESS_TOKEN = "gJvukELuaCOxRtd0jkucrdgIU15Cvf421lQWjRZv6+08RhE97ZPtbdwQUZ8S/JMBU3X+cTM8afrFoKdpHNGjo7EmXoO8Qs3IYh+87PGU6vM1YK5D7QF+FE5VM6ko73gk7dbMb+yUCVPcb+edMFhq+QdB04t89/1O/w1cDnyilFU="

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)


# タイマー機能(Ryu)
def timer():

    return render_template("time.html")


def message_send(username):

    conn = sqlite3.connect("thank.db", check_same_thread=False)
    db = conn.cursor()

    # Javascriptからデータを受け取り、辞書から各データを取り出す
    data = request.get_json()
    elapsedTime = data['elapsedTime']
    housework_name = data['housework_name']
    partner_username = data['partner_username']

    # ポイント計算
    db.execute("SELECT point FROM users WHERE name = ?", (username, ))
    old_point = db.fetchall()[0][0]
    print("ここまでのポイント", old_point, username)
    new_point = old_point + elapsedTime
    db.execute("UPDATE users SET point = ? WHERE name = ?", (new_point, username))
    conn.commit()


    # [0]['name']をつけないと、[{'name': 'Ryu test'}, {'name': 'aaaa'}]という感じで全ての値が出てきちゃう
    # そのため、1つ目のデータのnameに格納されている値を取ってくるとGood!

    db.execute("SELECT id FROM users WHERE name = ?", (partner_username,))  # javascriptはクライアントサイド→sqliteを普通には動かせない→pythonでやることに
    partner_user_id = db.fetchall()[0][0]
    print(partner_user_id, elapsedTime, housework_name)

    messages = TextSendMessage(text=f"{username}さんが{housework_name}を{elapsedTime}分しました！\n\n"
                                    f"ありがとうを送りましょう☺\n\n"
                                    f"http://127.0.0.1:5000/point") 

    line_bot_api.push_message(partner_user_id, messages)
    return redirect('/home') 


if __name__ == "__main__":
    app.run()
