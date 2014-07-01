from pymongo import MongoClient
db = MongoClient().packet_db
db.connection.drop_database('packet_db')
