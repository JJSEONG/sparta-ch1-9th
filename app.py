from flask import Flask, render_template, request, redirect, url_for, Blueprint
from pymongo import MongoClient
import time
import jwt
import schedule
import items
import user
import secret
import scraping

app = Flask(__name__)

app.register_blueprint(items.blue_items)
app.register_blueprint(user.blue_user)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/image/profile_pics"

key_list = {
    'MongoKey': secret.mongo_db_key,
    'SECRET_KEY': secret.jWT_KEY
}

SECRET_KEY = key_list['SECRET_KEY']
client = MongoClient(key_list['MongoKey'])
db = client.dbsparta
userCollection = db.users

scraping.scheduling()


@app.route('/')
def home():
    # 토큰 값 가져오기.
    token_receive = request.cookies.get('mytoken')
    try:
        # 토큰 해독 => 있으면 그대로 진행 / 없으면 except로 이동.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        cursor = dict(userCollection.find_one({"username": payload["id"]},
                                              {"_id": 0, "profile_name": 1, "profile_pic": 1}))

        return render_template('index.html', user=cursor)  # JWT 있는 Case
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template('user/login.html')  # JWT 없는 Case


# 매 Request 마다 JWT 토큰 체크 Handler
@app.before_request
def before_each():
    if request.cookies.get('mytoken') is None \
            and request.path.find('login') == -1 \
            and request.path.find('sign_in') == -1 \
            and request.path.find('sign_up') == -1 \
            and request.path.find('/static/') == -1:
        return redirect(url_for('user.login'))


# @app.route('/update_like', methods=['POST'])
# def update_like():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         # 좋아요 수 변경
#         return jsonify({"result": "success", 'msg': 'updated'})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=8000, debug=True)



while True:
    schedule.run_pending()
    time.sleep(1)

