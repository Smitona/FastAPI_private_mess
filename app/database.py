from pymongo import mongo_client, ASCENDING


client = mongo_client.MongoClient('localhost', 27017)

try:
    conn = client.server_info()
    print(f'Connected to MongoDB {conn.get("version")}')
except Exception:
    print('Unable to connect to the MongoDB server.')

db = client.test_db

users = db.users
messages = db.messages