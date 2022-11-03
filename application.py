import sqlite3
import jwt
import json
import requests
from flask import Flask, redirect, render_template, request, session
from datetime import timedelta
from linebot import LineBotApi
from linebot.models import TextSendMessage
from timer import timer, message_send
from friend import friend_index, search, add, delete

app = Flask(__name__)

#  sessionに関する設定
app.secret_key = "silvia"  #  sessionに格納する情報の暗号化
app.templated_auto_reload = True  #  render_templateで返すHTMLが動的に変化できるように
app.permanent_session_lifetime = timedelta(days=1)

#LINEのapiを使う(セキュリティ上の問題のため、利用時はLINE DEVELOPERSから値を代入する)
LINE_CHANNEL_ID = "1656842878"
LINE_CHANNEL_SECRET = "df3afe8afd799325b833998ef5908fcc"
REDIRECT_URL = "https://presentthanks.pythonanywhere.com/login"

#  チャネルアクセストークンはhttps://developers.line.biz/console/channel/1656501143/messaging-apiから取得
LINE_CHANNEL_ACCESS_TOKEN = "gJvukELuaCOxRtd0jkucrdgIU15Cvf421lQWjRZv6+08RhE97ZPtbdwQUZ8S/JMBU3X+cTM8afrFoKdpHNGjo7EmXoO8Qs3IYh+87PGU6vM1YK5D7QF+FE5VM6ko73gk7dbMb+yUCVPcb+edMFhq+QdB04t89/1O/w1cDnyilFU="
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)


# ログイン画面
@app.route("/", methods=["GET"])
def index():
    return render_template("login.html",
                          random_state="silvia",
                          channel_id=LINE_CHANNEL_ID,
                          redirect_url=REDIRECT_URL)


#  LINEログインの処理
@app.route("/login", methods=["GET", "POST"])
def line_login():

    conn = sqlite3.connect("thank.db")
    cur = conn.cursor()

    # LINEの認可コードを取得する
    request_code = request.args["code"]
    uri_access_token = "https://api.line.me/oauth2/v2.1/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data_params = {
        "grant_type": "authorization_code",
        "code": request_code,
        "redirect_uri": REDIRECT_URL,
        "client_id": LINE_CHANNEL_ID,
        "client_secret": LINE_CHANNEL_SECRET
    }

    # アクセストークンを取得するためにリクエストを送る
    response_post = requests.post(uri_access_token, headers=headers, data=data_params)

    #  LINEプロフィール情報取得のためにid_tokenを取得
    line_id_token = json.loads(response_post.text)["id_token"]

    # ペイロード部分をデコードすることで、ユーザ情報を取得する(デコード=異なる形式に変換されたデジタルデータを、元の状態に戻すこと)
    decoded_id_token = jwt.decode(line_id_token,
                                  LINE_CHANNEL_SECRET,
                                  audience=LINE_CHANNEL_ID,
                                  issuer='https://access.line.me',
                                  algorithms=['HS256'])

    # LINEの名前とidを取得
    name = decoded_id_token["name"]
    line_id = decoded_id_token["sub"]

    # login時にsessionの継続を開始
    session.permanent = True
    session["id"] = line_id

    # 登録されたユーザーかを確かめる(ログインしたことがあれば、データベースに情報は入っている)
    cur.execute("SELECT * FROM users WHERE id = ?", (line_id, ))

    #  初ログインの場合(取得したデータが空の場合)、データベースにユーザー情報を格納(ポイントは0にする)
    if cur.fetchall() == []:

        cur.execute("INSERT INTO users (id, name, point) VALUES (?, ?, 0);", (line_id, name))
        conn.commit()

    conn.close()
    return redirect("/home")


@app.route("/home", methods=["GET", "POST"])
def home():

    conn = sqlite3.connect("thank.db")
    cur = conn.cursor()

    if 'id' not in session:
        return redirect('/')

    else:
        # 現在login中のユーザー名、point、友人の名前を取得する
        cur.execute("SELECT name FROM users WHERE id = ?", (session["id"], ))
        username = cur.fetchall()
        cur.execute("SELECT point FROM users WHERE id = ?", (session["id"], ))
        now_points = cur.fetchall()
        cur.execute("SELECT name FROM users WHERE id IN (SELECT partner_id FROM friends WHERE user_id = ?)", (session["id"], ))
        friends_name = cur.fetchall()

        conn.close()
        return render_template("home.html", username=username, point=now_points, friends_name=friends_name)


@app.route('/timer')
def foreign_timer():
    if 'id' not in session:
        return redirect('/')

    else:
        return timer()


# ライン通知を送る(外部ファイルの関数message_sendを実行)
@app.route('/message-send', methods=["GET", "POST"])
def foreign_message_send():
    if 'id' not in session:
        return redirect('/')

    else:
        conn = sqlite3.connect("thank.db")
        cur = conn.cursor()

        #  現在ログイン中のユーザー名を取得
        cur.execute("SELECT name FROM users WHERE id = ?", (session["id"],))
        username = cur.fetchall()[0][0]

        conn.close()
        return message_send(username)


@app.route("/point", methods=["GET", "POST"])
def point():
    if 'id' not in session:
        return redirect('/')

    else:
        conn = sqlite3.connect("thank.db")
        cur = conn.cursor()

        if request.method == 'GET':
            #  現在ログイン中のユーザーのフレンドを取得
            cur.execute("SELECT name FROM users WHERE id IN (SELECT partner_id FROM friends WHERE user_id = ?)", (session["id"],))
            friends_name = cur.fetchall()

            conn.close()
            return render_template("point.html", friends_name=friends_name)

        else:
            # point.jsからJSONデータを受け取り、各データを取り出す
            data = request.get_json()
            add_point = data['thank_you']
            selected_friend_name = data['friend_name']

            # ありがとうポイントを送るパートナーのidを取得
            cur.execute("SELECT id FROM users WHERE name = ?", (selected_friend_name,))
            selected_friend_id = cur.fetchall()[0][0]

            # ありがとうポイントを送るパートナーの現在のポイントを取得
            cur.execute("SELECT point FROM users WHERE id = ?", (selected_friend_id,))
            old_point = cur.fetchall()[0][0] 
            
            # ポイントの計算と更新
            result_point = add_point + old_point
            cur.execute("UPDATE users SET point = ? WHERE id = ?", (result_point, selected_friend_id))
            conn.commit()

            conn.close()
            return redirect('/home')


@app.route("/point-message-send", methods=["GET", "POST"])
def point_message_send():
    conn = sqlite3.connect("thank.db")
    cur = conn.cursor()

    # point.jsからJSONデータを受け取り、各データを取り出す
    data = request.get_json()
    thankyou_point = data['thankyou_point']
    friend_name = data['friend_name']

    cur.execute("SELECT name FROM users WHERE id = ?", (session["id"],))
    username = cur.fetchall()[0][0]

    cur.execute("SELECT id FROM users WHERE name = ?", (friend_name,))
    partner_user_id = cur.fetchall()[0][0]

    #  LINEメッセージの生成と送信
    messages = TextSendMessage(text=f"{username}さんから\n\n"
                                    f"{thankyou_point}ありがとうポイントが届きました！\n\n")
    
    line_bot_api.push_message(partner_user_id, messages)
    
    conn.close()
    return redirect('/home')


# フレンドリストの表示
@app.route('/friend', methods = ['GET', 'POST'])
def foreign_friend_index():

    if 'id' not in session:
        return redirect('/')

    return friend_index()


# フレンド検索機能
@app.route('/search', methods = ['GET', 'POST'])
def foreign_search():

    if 'id' not in session:
        return redirect('/')

    return search()


# フレンド追加機能
@app.route('/add', methods = ['GET', 'POST'])
def foreign_add():

    if 'id' not in session:
        return redirect('/')

    return add()


# フレンド削除機能
@app.route('/delete', methods = ['GET', 'POST'])
def foreign_delete():

    if 'id' not in session:
        return redirect('/')

    return delete()


# ログアウト機能
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)  #  公開のときFalseにする
