from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
import secret

# DB key 노출을 막기 위한 간단 설정!
#    - DB 설정을 위해서 root 디렉터리에 secret.py를 생성
#    - mongo_db_key = "주소" 입력

key_list = {
    'MongoKey': secret.mongo_db_key
}

# MongoDBConnection
client = MongoClient(key_list['MongoKey'])
db = client.dbsparta
todoCollection = db.todolist
pkCollection = db.pks

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=8002, debug=True)