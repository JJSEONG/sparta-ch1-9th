from flask import render_template, request, jsonify, Blueprint
from bson.json_util import dumps
from bson import ObjectId
from pymongo import MongoClient
import secret

blue_items = Blueprint("item", __name__)
key_list = {
    'MongoKey': secret.mongo_db_key
}

# MongoDBConnection
client = MongoClient(key_list['MongoKey'])
db = client.dbsparta
itemCollection = db.items


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
    return {'items': dumps(item_list), "count": len(item_list)}


def get_items_by_store(store, key, last_id):
    item_list = list(itemCollection.find({"_id": {"$gt": ObjectId(last_id)},
                                          "store": store},
                                         {'store': 1,
                                          'image': 1,
                                          'title': 1,
                                          'price': 1,
                                          'like': 1,
                                          'array': -1})
                     .sort(key, 1)
                     .limit(12))
    return {'items': dumps(item_list), "count": len(item_list)}


@blue_items.route('/items/like')
def like():
    return


@blue_items.route('/item/<item_id>')
def get_item(item_id):
    item = itemCollection.find_one({"_id": {"$eq": ObjectId(item_id)}})
    return render_template("item.html", item=item)


def add_review(item_id, review_id):
    itemCollection.update_one({"_id": {"$eq": ObjectId(item_id)}},
                              {"$push": {"reviews": review_id}})
