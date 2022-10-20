import sqlite3
import jwt
import json
import requests
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from datetime import timedelta
from timer import timer, message_send
from friend import friend_index, search, add, delete
from linebot import LineBotApi
from linebot.models import TextSendMessage


app = Flask(__name__)

app.config["SECRET_KEY"] = "silvia"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

conn = sqlite3.connect("thank.db", check_same_thread=False)


#LINEのapiを使う
#セキュリティ上の問題のため、利用時はLINE DEVELOPERSから値を代入する
LINE_CHANNEL_ID = "チャネルID"
LINE_CHANNEL_SECRET = "チャネルシークレット"
REDIRECT_URL = "https://presentthanks.pythonanywhere.com/login"

#  チャネルアクセストークンはhttps://developers.line.biz/console/channel/1656501143/messaging-apiから取得
LINE_CHANNEL_ACCESS_TOKEN = "チャネルアクセストークン"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# 初期のログイン画面
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html",
                          random_state="silvia",
                          channel_id=LINE_CHANNEL_ID,
                          redirect_url=REDIRECT_URL)


@app.route("/login", methods=["GET", "POST"])
def line_login():

    db = conn.cursor()

    # loginしたら、sessionの継続がスタート
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=1)

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

    # トークンを取得するためにリクエストを送る
    response_post = requests.post(uri_access_token, headers=headers, data=data_params)
    line_id_token = json.loads(response_post.text)["id_token"]

    # ペイロード部分をデコードすることで、ユーザ情報を取得する
    # デコードとは、異なる形式に変換されたデジタルデータを、元の状態に戻すこと
    decoded_id_token = jwt.decode(line_id_token,
                                  LINE_CHANNEL_SECRET,
                                  audience=LINE_CHANNEL_ID,
                                  issuer='https://access.line.me',
                                  algorithms=['HS256'])

    # LINEの名前やid情報をここで取得する
    name = decoded_id_token["name"]
    picture = decoded_id_token["picture"]
    line_id = decoded_id_token["sub"]

    # session用のidとしてline_idを設定(持続は1日)
    session["id"] = line_id

    # 登録されたユーザーかを確かめる(ログインしたことがあれば、データベースに情報は入っている)
    db.execute("SELECT * FROM users WHERE id = ?", (line_id, ))
    is_user_existed = db.fetchall()

    #  初登録の場合、データベースにLINEの情報を格納する(ポイントは0にする)
    if is_user_existed == []:

        db.execute("INSERT INTO users (id, name, image_url, point) VALUES (?, ?, ?, 0);", (line_id, name, picture))
        conn.commit()

        return redirect("/home")
    
    else:
        return redirect("/home")


@app.route("/home", methods=["GET", "POST"])
def home():

    conn = sqlite3.connect("thank.db", check_same_thread=False)
    db = conn.cursor()

    if 'id' not in session:
        return redirect('/')

    else:
        # 現在login中のユーザーの名前を取得する
        db.execute("SELECT name FROM users WHERE id = ?", (session["id"], ))
        username = db.fetchall()

        # 現在login中のユーザーのpointを取得する
        db.execute("SELECT point FROM users WHERE id = ?", (session["id"], ))
        now_points = db.fetchall()
        
        # 現在login中のユーザーの友人の名前を取得する
        db.execute("SELECT name FROM users WHERE id IN (SELECT partner_id FROM friends WHERE user_id = ?)", (session["id"], ))
        
        # フレンドが登録されていない場合、データは存在しない
        try:
            friends_name = db.fetchall()
        except IndexError:
            pass

        conn.close()

        return render_template("home.html", username=username, point=now_points, friends_name=friends_name)


@app.route('/timer')
def foreign_timer():

    if 'id' not in session:
        return redirect('/')

    else:
        return timer()


# ライン通知を送る機能
@app.route('/message-send', methods=["GET", "POST"])
def foreign_message_send():

    conn = sqlite3.connect("thank.db", check_same_thread=False)
    db = conn.cursor()

    if 'id' not in session:
        return redirect('/')

    else:
        db.execute("SELECT name FROM users WHERE id = ?", (session["id"],))
        username = db.fetchall()[0][0]
        return message_send(username)


@app.route("/point", methods=["GET", "POST"])
def point():

    conn = sqlite3.connect("thank.db", check_same_thread=False)
    db = conn.cursor()

    if 'id' not in session:
        return redirect('/')

    else:
        if request.method == 'GET':
            db.execute("SELECT name FROM users WHERE id IN (SELECT partner_id FROM friends WHERE user_id = ?)", (session["id"],))
            
            #  フレンドが登録されていない場合、データは存在しない
            try:
                friends_name = db.fetchall()
            except IndexError:
                friends_name = db.fetchall()

            return render_template("point.html", friends_name=friends_name)

        else:
            # Javascriptからデータを受け取り、各データを取り出す
            data = request.get_json()
            add_point = data['thank_you']
            selected_friend_name = data['friend_name']

            # 選択されたフレンドのidを取得
            db.execute("SELECT id FROM users WHERE name = ?", (selected_friend_name,))
            selected_friend_id = db.fetchall()[0][0]

            # 選択されたフレンドの現在のポイントを取得
            db.execute("SELECT point FROM users WHERE id = ?", (selected_friend_id,))
            old_point = db.fetchall()[0][0] 
            
            # ポイント計算
            result_point = add_point + old_point

            # ポイントの更新
            db.execute("UPDATE users SET point = ? WHERE id = ?", (result_point, selected_friend_id))
            conn.commit()

            return redirect('/home')


@app.route("/point-message-send", methods=["GET", "POST"])
def point_message_send():
    conn = sqlite3.connect("thank.db", check_same_thread=False)
    db = conn.cursor()

    # Javascriptからデータを受け取り、各データを取り出す
    data = request.get_json()
    thankyou_point = data['thankyou_point']
    friend_name = data['friend_name']

    db.execute("SELECT name FROM users WHERE id = ?", (session["id"],))
    username = db.fetchall()[0][0]

    db.execute("SELECT id FROM users WHERE name = ?", (friend_name,))
    partner_user_id = db.fetchall()[0][0]

    #  LINEメッセージの生成と送信
    messages = TextSendMessage(text=f"{username}さんから\n\n"
                                    f"{thankyou_point}ありがとうポイントが届きました！\n\n")
    
    line_bot_api.push_message(partner_user_id, messages)
    
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
    app.run(debug=True)
