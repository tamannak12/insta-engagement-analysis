import sys
import os

# Ensure `src` is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import mysql.connector
from src.config.db import get_db  # Use absolute import

db = get_db()


# MySQL Connection
mysql_conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="MySQL@123",
    database="insta_engagement"
)
cursor = mysql_conn.cursor(dictionary=True)

# Migrate Profiles
cursor.execute("SELECT * FROM instagram_profiles")
profiles = cursor.fetchall()
for profile in profiles:
    username = profile["username"]
    
    # Get bio links
    cursor.execute("SELECT title, url FROM bio_links WHERE username = %s", (username,))
    profile["bio_links"] = cursor.fetchall()
    
    db.profiles.insert_one(profile)

# Migrate Posts
cursor.execute("SELECT * FROM instagram_posts")
posts = cursor.fetchall()
for post in posts:
    post_id = post["id"]
    
    # Get comments
    cursor.execute("SELECT username, comment FROM instagram_comments WHERE post_id = %s", (post_id,))
    post["comments"] = cursor.fetchall()
    
    db.posts.insert_one(post)

print("Migration completed successfully!")

cursor.close()
mysql_conn.close()
