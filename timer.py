import json
import sqlite3
from flask import Flask, render_template, request, redirect
from linebot import LineBotApi
from linebot.models import TextSendMessage

app = Flask(__name__)

# セキュリティ上の問題のため、利用時はLINE DEVELOPERSから値を代入する
LINE_CHANNEL_ACCESS_TOKEN = "チャネルアクセストークン"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)


def timer():
    return render_template("time.html")


#  家事時間計測終了後の処理
def message_send(username):
    conn = sqlite3.connect("thank.db")
    cur = conn.cursor()

    # time.jsからJSONを受け取り、データを取り出す
    data = request.get_json()
    elapsedTime = data['elapsedTime']
    housework_name = data['housework_name']
    partner_username = data['partner_username']

    # ポイントの加算と更新
    cur.execute("SELECT point FROM users WHERE name = ?", (username, ))
    old_point = cur.fetchall()[0][0]

    #  1分ごとに1ポイント加算される
    new_point = old_point + elapsedTime

    cur.execute("UPDATE users SET point = ? WHERE name = ?", (new_point, username))
    conn.commit()

    #  通知を送るパートナーのidを取得
    cur.execute("SELECT id FROM users WHERE name = ?", (partner_username,))
    partner_user_id = cur.fetchall()[0][0]

    #  LINEメッセージ生成と送信
    messages = TextSendMessage(text=f"{username}さんが{housework_name}を{elapsedTime}分しました！\n\n"
                                    f"ありがとうを送りましょう☺\n\n"
                                    f"https://presentthanks.pythonanywhere.com/point") 

    line_bot_api.push_message(partner_user_id, messages)

    conn.close()
    return redirect('/home') 
