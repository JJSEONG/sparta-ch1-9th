from flask import Blueprint
from pymongo import MongoClient
import secret


# DB key 노출을 막기 위한 간단 설정!
#    - DB 설정을 위해서 root 디렉터리에 secret.py를 생성
#    - mongo_db_key = "주소" 입력
class DB(object):
    URI = secret.mongo_db_key

    @staticmethod
    def init():
        client = MongoClient(DB.URI)
        DB.DATABASE = client.dbsparta

    @staticmethod
    def insert(collection, data):
        DB.DATABASE[collection].insert(data)

    @staticmethod
    def find_one(collection, query):
        return DB.DATABASE[collection].find_one(query)