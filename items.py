from flask import render_template, request, jsonify, Blueprint
from bson.json_util import dumps
from bson import ObjectId
from pymongo import MongoClient
import secret
import jwt

blue_items = Blueprint("item", __name__)
key_list = {
    'MongoKey': secret.mongo_db_key,
    'SECRET_KEY': secret.JWT_KEY
}

# MongoDBConnection
client = MongoClient(key_list['MongoKey'])
db = client.dbsparta
itemCollection = db.items
likeCollection = db.like_items


@blue_items.route('/items', methods=['GET'])
def get_items():
    store = request.args.get('store')
    sort_key = request.args.get('sort_key')
    last_id = request.args.get('last_id')
    search = request.args.get('search')

    if len(store) < 1:
        item_collection = get_items_all(sort_key, last_id, search)
    else:
        item_collection = get_items_by_store(store, sort_key, last_id)

    return jsonify(item_collection)


def get_items_all(key, last_id, search_keyword):
    if key == '_id':
        item_list = list(itemCollection.find({"_id": {"$gt": ObjectId(last_id)},
                                              "title": {"$regex": search_keyword}},
                                             {'store': 1,
                                              'image': 1,
                                              'title': 1,
                                              'price': 1,
                                              'like': 1,
                                              'array': -1})
                         .sort(key, 1)
                         .limit(12))

    else:
        print(key)
        item_list = list(itemCollection.find({"_id": {"$gt": ObjectId(last_id)},
                                              "title": {"$regex": search_keyword}},
                                             {'store': 1,
                                              'image': 1,
                                              'title': 1,
                                              'price': 1,
                                              'like': 1,
                                              'review_count': {'$size': "$reviews"}})
                         .sort(key, -1)
                         .limit(12))
        print('get_items_all by else')
        print(item_list)
    return {'items': dumps(item_list), "count": len(item_list)}


def get_items_by_store(store, key, last_id):
    if key == '_id':
        item_list = list(itemCollection.find({"_id": {"$gt": ObjectId(last_id)},
                                              "store": store},
                                             {'store': 1,
                                              'image': 1,
                                              'title': 1,
                                              'price': 1,
                                              'like': 1,
                                              'array': -1,
                                              'review_count': {'$size': "$array"}})
                         .sort(key, 1)
                         .limit(12))
    else:
        item_list = list(itemCollection.find({"_id": {"$gt": ObjectId(last_id)},
                                              "store": store},
                                             {'store': 1,
                                              'image': 1,
                                              'title': 1,
                                              'price': 1,
                                              'like': 1,
                                              'array': -1,
                                              'review_count': {'$size': "$array"}})
                         .sort(key, -1)
                         .limit(12))
    return {'items': dumps(item_list), "count": len(item_list)}


@blue_items.route('/items/like', methods=["POST"])
def like():
    token_receive = request.cookies.get('mytoken')
    item_id = request.form.get('item_id')
    try:
        payload = jwt.decode(token_receive, key_list['SECRET_KEY'], algorithms=['HS256'])
        username = payload["id"]
        like_result = likeCollection.find_one({"username": {"$eq": username},
                                               "item_list": {"$eq": item_id}})
        if like_result is None:
            likeCollection.update_one({"username": {"$eq": username}},
                                      {"$push": {"item_list": item_id}})
            itemCollection.update_one({"_id": {"$eq": ObjectId(item_id)}}, {"$inc": {"like": 1}})
            result = 1
        else:
            likeCollection.update_one({"username": {"$eq": username}},
                                      {"$pull": {"item_list": item_id}})
            itemCollection.update_one({"_id": {"$eq": ObjectId(item_id)}}, {"$inc": {"like": -1}})
            result = 0
        return jsonify({"result": "success", 'inc': result})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail"})


@blue_items.route('/user/like_items', methods=["GET"])
def user_like_list():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, key_list['SECRET_KEY'], algorithms=['HS256'])
        result = likeCollection.find_one({"username": payload["id"]},
                                         {"_id": 0, "item_list": 1})
        return jsonify({"result": "success", "item_list": result})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({"result": "fail"})


@blue_items.route('/item/<item_id>')
def get_item(item_id):
    item = itemCollection.find_one({"_id": {"$eq": ObjectId(item_id)}})
    return render_template("item.html", item=item)


def add_review(item_id, review_id):
    itemCollection.update_one({"_id": {"$eq": ObjectId(item_id)}},
                              {"$push": {"reviews": review_id}})
