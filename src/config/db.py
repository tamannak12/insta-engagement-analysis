import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

DB_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "instagram_db")

client = MongoClient(DB_URI)
db = client[DB_NAME]

def get_db():
    return db