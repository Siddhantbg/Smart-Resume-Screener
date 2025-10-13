from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_client():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("MongoDB URI not configured")
        return None
    
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=3000)
        client.admin.command('ping')
        print("MongoDB connected")
        return client
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return None

def get_database():
    client = get_db_client()
    if not client:
        return None
    db_name = os.getenv("DB_NAME", "smart_resume_screener")
    return client[db_name]

def close_db_client(client):
    if client:
        try:
            client.close()
        except:
            pass
