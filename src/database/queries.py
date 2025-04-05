from pymongo import ASCENDING
from src.config.db import get_db

db = get_db()

def get_profile_by_username(username):
    return db.profiles.find_one({"username": username})

def get_all_profiles(limit=15, offset=0):
    return list(db.profiles.find().sort("follower_count", ASCENDING).skip(offset).limit(limit))

def search_profiles(search_term, limit=10):
    return list(db.profiles.find(
        {"$or": [{"username": {"$regex": search_term, "$options": "i"}},
                 {"full_name": {"$regex": search_term, "$options": "i"}}]}
    ).limit(limit))

def get_posts_by_username(username, limit=15):
    return list(db.posts.find({"username": username}).sort("timestamp", ASCENDING).limit(limit))
