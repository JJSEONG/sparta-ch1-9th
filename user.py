from pymongo import MongoClient
import jwt
import datetime
import hashlib
import secret
from flask import Flask, render_template, jsonify, request, redirect, url_for, Blueprint
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

blue_user = Blueprint("user", __name__)

key_list = {
    'MongoKey': secret.mongo_db_key,
    'SECRET_KEY': secret.JWT_KEY,
    'JWT_ACCESS_EXPIRES': secret.JWT_ACCESS_EXPIRES,
    'JWT_REFRESH_EXPIRES': secret.JWT_REFRESH_EXPIRES
}

SECRET_KEY = key_list['SECRET_KEY']
ACCESS_EXPIRES = key_list['JWT_ACCESS_EXPIRES']
REFRESH_EXPIRES = key_list['JWT_REFRESH_EXPIRES']

client = MongoClient(key_list['MongoKey'])
db = client.dbsparta


@blue_user.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('user/login.html', msg=msg)


@blue_user.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('user/user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("."))


@blue_user.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@blue_user.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    user_doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "image/profile_pics/basic_profile.png",  # 프로필 사진 기본 이미지
        "profile_info": "",  # 프로필 한 마디
        "like": 0,           # 받은 좋아요 수
    }

    # 회원가입 시 전용 좋아요 리스트도 생성.
    like_doc = {
        "username": username_receive,
        "item_list": []
    }
    db.users.insert_one(user_doc)
    db.like_items.insert_one(like_doc)
    return jsonify({'result': 'success'})


@blue_user.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@blue_user.route('/sign_out', methods=['POST'])
def sign_out():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@blue_user.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "profile_name": name_receive,
            "profile_info": about_receive
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = "image/profile_pics/"
            print(username + "." + extension)
            file.save("./static/" + file_path, username + "." + extension)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({'username': payload['id']}, {'$set': new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
