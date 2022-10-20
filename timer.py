import json
import sqlite3
from flask import Flask, render_template, request, redirect
from linebot import LineBotApi
from linebot.models import TextSendMessage


db = sqlite3.connect("thank.db", check_same_thread=False)

app = Flask(__name__)

# 以下、LINE bot関連の情報
#  チャネルアクセストークンはhttps://developers.line.biz/console/channel/1656501143/messaging-apiから取得
LINE_CHANNEL_ACCESS_TOKEN = "gJvukELuaCOxRtd0jkucrdgIU15Cvf421lQWjRZv6+08RhE97ZPtbdwQUZ8S/JMBU3X+cTM8afrFoKdpHNGjo7EmXoO8Qs3IYh+87PGU6vM1YK5D7QF+FE5VM6ko73gk7dbMb+yUCVPcb+edMFhq+QdB04t89/1O/w1cDnyilFU="

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)


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

    new_point = old_point + elapsedTime

    #  ポイント更新
    db.execute("UPDATE users SET point = ? WHERE name = ?", (new_point, username))
    conn.commit()

    #  通知を送る友人のidを取得
    db.execute("SELECT id FROM users WHERE name = ?", (partner_username,))
    partner_user_id = db.fetchall()[0][0]

    #  タイマー計測終了後にLINEメッセージ生成と送信
    messages = TextSendMessage(text=f"{username}さんが{housework_name}を{elapsedTime}分しました！\n\n"
                                    f"ありがとうを送りましょう☺\n\n"
                                    f"https://presentthanks.pythonanywhere.com/point") 

    line_bot_api.push_message(partner_user_id, messages)

    return redirect('/home') 
