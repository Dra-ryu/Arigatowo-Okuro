import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from datetime import timedelta
import json
import requests
import jwt
from timer import timer, message_send  # timer.pyを使えるように
from frend import friend_index, search, add, delete  # frend.pyを使えるように

# beautiful soup用
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

app.config["SECRET_KEY"] = "silvia"
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Configure session to use filesystem (instead of signed cookies)
#　cookie内に格納ではなく、ローカルファイルシステムに格納するようにflaskを構成
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///thank.db")


#LINEのapi機能を使う
LINE_CHANNEL_ID = "1656842878"
LINE_CHANNEL_SECRET = "df3afe8afd799325b833998ef5908fcc"
REDIRECT_URL = "https://ide-7ebceea5200d4ec6b5f68152dd2b843c-8080.cs50.ws/login"


# 初期のログイン画面
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html",
                          random_state="silvia",
                          channel_id=LINE_CHANNEL_ID,
                          redirect_url=REDIRECT_URL)


@app.route("/login", methods=["GET", "POST"])
def line_login():

    # loginしたら、sessionの継続がスタートする
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

    # 現在login中のユーザーの名前を取得する
    username = db.execute("SELECT name FROM users WHERE id = ?", session["id"])

    # 現在login中のユーザーのpointを取得する
    now_points = db.execute("SELECT point FROM users WHERE id = ?", line_id)

    # 現在login中のユーザーの友人の名前を取得する
    friends_name = db.execute("SELECT name FROM users WHERE id IN (SELECT partner_id FROM friends WHERE user_id = ?)", session["id"])

    # 初めてのログインか、ログイン済みかを確かめる(ログインしたことがあれば、データベースに情報は入っているはず)
    check_existance = db.execute("SELECT * FROM users WHERE id = ?", session["id"])

    # session中のidの情報がデータベースに格納されていた場合(再ログインの場合)
    if check_existance:
        return redirect("/home")

    # 初ログインの場合
    else:
        # データベースにLINEの情報を格納する(ポイントは0にする)
        db.execute("INSERT INTO users (id, name, image_url, point) VALUES (?, ?, ?, 0)", line_id, name, picture)

        # ホーム画面にredirect(/home)のルートで値を取得できるので、渡さなくても大丈夫
        return redirect("/home")


@app.route("/home", methods=["GET", "POST"])
def home():
    # sessionが切れていたら、ログイン画面に戻る
    if 'id' not in session:
        return redirect('/')

    else:
        # 現在login中のユーザーの名前を取得する
        username = db.execute("SELECT name FROM users WHERE id = ?", session["id"])

        # 現在login中のユーザーのpointを取得する
        now_points = db.execute("SELECT point FROM users WHERE id = ?", session["id"])

        # 現在login中のユーザーの友人の名前を取得する
        friends_name = db.execute("SELECT name FROM users WHERE id IN (SELECT partner_id FROM friends WHERE user_id = ?)", session["id"])

        # home.htmlを表示する
        return render_template("home.html", username=username, point=now_points, friends_name=friends_name)


# 以下timer機能
@app.route('/timer')
def foreign_timer():

    # sessionが切れていたら、ログイン画面に戻る
    if 'id' not in session:
        return redirect('/')

    else:
        return timer()  # timer.pyのtimer()を呼び出している

# ラインの通知を送る機能
@app.route('/message-send', methods=["GET", "POST"])
def foreign_message_send():

    # sessionが切れていたら、ログイン画面に戻る
    if 'id' not in session:
        return redirect('/')

    else:
        username = db.execute("SELECT name FROM users WHERE id = ?", session["id"])[0]['name']
        user_id = session["id"]
        return message_send(username)  # usernameを引数に


# 以下ポイント機能
@app.route("/point", methods=["GET", "POST"])
def point():
    # sessionが切れていたら、ログイン画面に戻る
    if 'id' not in session:
        return redirect('/')

    else:
        if request.method == 'GET':
            friends_name = db.execute("SELECT name FROM users WHERE id IN (SELECT partner_id FROM friends WHERE user_id = ?)", session["id"])
            return render_template("point.html", friends_name=friends_name)

        else:
            data = request.get_json()
            add_point = data['thank_you']
            selected_friend_name = data['friend_name']

            # 選択されたフレンドのidを取得
            selected_friend_id = db.execute("SELECT id FROM users WHERE name = ?", selected_friend_name)[0]["id"]

            # 選択されたフレンドの現在のポイントを取得
            old_point = db.execute("SELECT point FROM users WHERE id = ?", selected_friend_id)[0]["point"]

            # ポイント計算
            result_point = add_point + old_point

            # 追加後のポイントにUPDATE
            db.execute("UPDATE users SET point = ? WHERE id = ?", result_point, selected_friend_id) #point更新

            return redirect('/point_sent')


@app.route("/point_sent", methods=["GET", "POST"])
def message_sent():
    return render_template("point_sent.html")


# 以下フレンド機能
# フレンドリストの表示機能
@app.route('/friend', methods = ['GET', 'POST'])
def foreign_friend_index():

    # sessionが切れていたら、ログイン画面に戻る
    if 'id' not in session:
        return redirect('/')

    return friend_index()


# フレンド検索機能
@app.route('/search', methods = ['GET', 'POST'])
def foreign_search():

    # sessionが切れていたら、ログイン画面に戻る
    if 'id' not in session:
        return redirect('/')

    return search()

# フレンド追加機能
@app.route('/add', methods = ['GET', 'POST'])
def foreign_add():

    # sessionが切れていたら、ログイン画面に戻る
    if 'id' not in session:
        return redirect('/')

    return add()

# フレンド削除機能
@app.route('/delete', methods = ['GET', 'POST'])
def foreign_delete():

    # sessionが切れていたら、ログイン画面に戻る
    if 'id' not in session:
        return redirect('/')

    return delete()


# 以下ログアウト機能
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

