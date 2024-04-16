from pymongo import mongo_client


def get_db():
    client = mongo_client.MongoClient('localhost', 27017)

    try:
        conn = client.server_info()
        print(f'Connected to MongoDB {conn.get("version")}')
    except Exception:
        print('Unable to connect to the MongoDB server.')

    db = client.test_db
    return db


users = get_db().users
messages = get_db().messages
