from src.config.db import get_db

db = get_db()

def save_profile(data):
    """Insert or update a profile in MongoDB."""
    db.profiles.update_one({"username": data["username"]}, {"$set": data}, upsert=True)

def save_posts(username, posts):
    """Save Instagram posts along with comments."""
    for post in posts:
        db.posts.update_one({"_id": post["id"]}, {"$set": post}, upsert=True)

def save_comments(post_id, comments):
    """Update comments for a specific post."""
    db.posts.update_one({"_id": post_id}, {"$set": {"comments": comments}}, upsert=True)
