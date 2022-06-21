import requests
from flask import Flask, render_template, request, jsonify, Blueprint
from pymongo import MongoClient
from bson import ObjectId
import secret

items = Flask(__name__)
key_list = {
    'MongoKey': secret.mongo_db_key
}

# MongoDBConnection
client = MongoClient(key_list['MongoKey'])
db = client.dbsparta
itemCollection = db.items


@items.route('/items')
def get_items():
    store = "gs"
    sortKey = "like"
    last_id = 8
    # last_id = request.form["pageNum"]
    # if request.form["store"] is not None:
        # store = request.form["store"]

    item_list = list(itemCollection.find({"_id": {"$gt": ObjectId('62b1057004d67a7d09e9e229')}, "store": store})
                     .sort(sortKey)
                     .limit(8))
    return render_template("items.html", items=item_list)


@items.route('/item/<item_id>')
def get_item(item_id):
    item = itemCollection.find_one({"_id": {"$eq": ObjectId(item_id)}})
    print(item)
    return render_template("item.html", item=item)


if __name__ == '__main__':
    get_items()
    get_item()
