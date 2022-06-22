from bson import ObjectId
from bson.json_util import dumps
from pymongo import MongoClient
import jwt
from flask import Flask, render_template, jsonify, request, redirect, url_for, Blueprint
import secret
from items import add_review

blue_review = Blueprint("review", __name__)

key_list = {
    'MongoKey': secret.mongo_db_key,
    'SECRET_KEY': secret.JWT_KEY
}

SECRET_KEY = key_list['SECRET_KEY']
client = MongoClient(key_list['MongoKey'])
db = client.dbsparta


@blue_review.route('/review', methods=['POST'])
def reviewing():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅하기
        user_info = db.users.find_one({"username": payload["id"]})
        comment_receive = request.form["comment_give"]
        date_receive = request.form["date_give"]
        item_id = request.form['item_id']
        doc = {
            "username": user_info["username"],
            "profile_name": user_info["profile_name"],
            "profile_pic_real": user_info["profile_pic_real"],
            "comment": comment_receive,
            "date": date_receive,
            "item_id": item_id
        }
        review_id = db.reviews.insert_one(doc)
        add_review(item_id, str(review_id.inserted_id))
        return jsonify({"result": "success", 'msg': '포스팅 성공'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@blue_review.route("/reviews", methods=['GET'])
def get_reviews():
    token_receive = request.cookies.get('mytoken')
    last_id = request.args.get('last_id')
    item_id = request.args.get('item_id')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 포스팅 목록 받아오기
        reviews = list(db.reviews
                       .find({"_id": {"$gt": ObjectId(last_id)},
                              "item_id": {"$eq": item_id}})
                       .sort("date", -1)
                       .limit(4))
        for review in reviews:
            review["_id"] = str(review["_id"])
            review["count_heart"] = db.likes.count_documents({"review_id": review["_id"], "type": "heart"})
            review["heart_by_me"] = bool(db.likes.find_one({"review_id": review["_id"], "type": "heart", "username": payload['id']}))
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "reviews": reviews, "size": len(reviews)})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@blue_review.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # like collection에 넣기
        user_info = db.users.find_one({"username": payload["id"]})
        review_id_receive = request.form["review_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "review_id": review_id_receive,
            "username": user_info["username"],
            "type": type_receive
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"review_id": review_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@blue_review.route('/review', methods=['DELETE'])
def delete_review():
    review_id = request.form['review_id']
    review_info = db.reviews.find_one({"_id": ObjectId(review_id)})

    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    if review_info['username'] == payload['id']:
        res = db.reviews.delete_one({'_id': ObjectId(review_id)})
        print(res.deleted_count)
        print(res.raw_result)
        if res:
            return jsonify({'status': 200})
        else:
            return jsonify({'status': 400})
    else:
        return jsonify({'status': 401})


@blue_review.route('/myReviews', methods=['GET'])
def reviews_by_username():
    token_receive = request.cookies.get('mytoken')
    last_review_id = request.args.get('last_review_id')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload['id']
        reviews = list(db.reviews.find({"username": {"$eq": username}})
                       .sort('date', -1)
                       .limit(5))
        return jsonify({"result": "success", "reviews": dumps(reviews), "count": len(reviews)})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail"})