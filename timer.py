import json
import os
import requests
import sys
from cs50 import SQL  # SQLを使えるようにする
from flask import Flask, render_template, request, abort, redirect
from linebot import LineBotApi
from linebot.models import TextSendMessage
from flask_session import Session


db = SQL("sqlite:///thank.db")

app = Flask(__name__)

# 以下、LINE bot関連の情報

#  チャネルアクセストークンはhttps://developers.line.biz/console/channel/1656501143/messaging-apiから取得
LINE_CHANNEL_ACCESS_TOKEN = "ZOXAzvYEL3oXZ/8E5tb6ehMfUwLkhj5JygWXJ0IN//HYaOwnUmNxckv5KGbqvzGS6Q5NG5j+CkZsWHPIi3IJa2VotnXy+ewvO7NUQ1nW13qpfIcRHHsd6EObbCP0uh1DHVbSxq7Z/+BIT1wpTWG70wdB04t89/1O/w1cDnyilFU="

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)


# タイマー機能(Ryu)
def timer():

    return render_template("time.html")


def message_send(username):

    # Javascriptからデータを受け取り、辞書から各データを取り出す
    data = request.get_json()
    elapsedTime = data['elapsedTime']
    housework_name = data['housework_name']
    partner_username = data['partner_username']

    # ポイント計算
    old_point = db.execute("SELECT point FROM users WHERE name = ?", username)[0]["point"]
    new_point = old_point + elapsedTime
    db.execute("UPDATE users SET point = ? WHERE name = ?", new_point, username)


    # [0]['name']をつけないと、[{'name': 'Ryu test'}, {'name': 'aaaa'}]という感じで全ての値が出てきちゃう
    # そのため、1つ目のデータのnameに格納されている値を取ってくるとGood!

    partner_user_id = db.execute("SELECT id FROM users WHERE name = ?", partner_username)[0]["id"]  # javascriptはクライアントサイド→sqliteを普通には動かせない→pythonでやることに

    messages = TextSendMessage(text=f"{username}さんが{housework_name}を{elapsedTime}分しました！\n\n"
                                    f"ありがとうを送りましょう☺\n\n"
                                    f"https://ide-7ebceea5200d4ec6b5f68152dd2b843c-8080.cs50.ws/point") 

    line_bot_api.push_message(partner_user_id, messages=messages)
    return redirect('/home') 


if __name__ == "__main__":
    app.run()
