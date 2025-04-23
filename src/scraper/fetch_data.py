import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PROFILE_URL = os.getenv("SCRAPER_URL")  # Profile API URL
POSTS_URL = os.getenv("SCRAPER_Post_URL")  # Separate Posts API URL
API_KEY = os.getenv("SCRAPER_API_KEY")

HEADERS = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "instagram-scraper-api2.p.rapidapi.com"
}

def safe_get(data, *keys, default=None):
    """Safely retrieve nested dictionary keys."""
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
        if current is None:
            return default
    return current if current is not None else default

def fetch_instagram_posts(username):
    """Fetch Instagram posts using the separate post API."""
    querystring = {"username_or_id_or_url": username}
    
    try:
        response = requests.get(POSTS_URL, headers=HEADERS, params=querystring)
        response.raise_for_status()  # Raise exception for HTTP errors
        post_data = response.json().get("data", {}).get("items", [])
        
        posts = []
        for post in post_data:
            posts.append({
                "id": safe_get(post, "id"),
                "code": safe_get(post, "code"),
                "thumbnail_url": safe_get(post, "thumbnail_url"),
                "like_count": safe_get(post, "like_count", default=0),
                "comment_count": safe_get(post, "comment_count", default=0),
                "caption": safe_get(post, "caption", "text", default=""),
                "timestamp": safe_get(post, "taken_at_timestamp"),
                "comments": []  # Placeholder for comments
            })
        
        return posts
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Failed to fetch posts for {username}: {e}")
        return []

def fetch_comments_for_post(post_id):
    """Fetch comments for a specific Instagram post."""
    url = "https://instagram-scraper-api2.p.rapidapi.com/v1/comments"
    querystring = {"code_or_id_or_url": post_id, "sort_by": "popular"}

    try:
        response = requests.get(url, headers=HEADERS, params=querystring)
        response.raise_for_status()
        data = response.json().get("data", {})

        comments = data.get("items", [])
        comments_list = [
            {
                "user": comment.get("user", {}).get("username", "Unknown"),
                "text": comment.get("text", "No text")
            }
            for comment in comments
        ]

        return comments_list
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Failed to fetch comments for post {post_id}: {e}")
        return []

def fetch_instagram_data(username):
    """Fetch Instagram profile data and posts with comments."""
    querystring = {"username_or_id_or_url": username}

    try:
        # Fetch profile data
        response = requests.get(PROFILE_URL, headers=HEADERS, params=querystring)
        response.raise_for_status()
        data = response.json().get('data', {})

        # Fetch post data separately
        posts = fetch_instagram_posts(username)

        # Fetch comments for each post
        for post in posts:
            post["comments"] = fetch_comments_for_post(post["id"])

        return {
            "username": data.get("username"),
            "full_name": data.get("full_name"),
            "follower_count": data.get("follower_count"),
            "following_count": data.get("following_count"),
            "media_count": data.get("media_count"),
            "is_verified": data.get("is_verified"),
            "category": data.get("category"),
            "biography": data.get("biography"),
            "profile_pic_url_hd": data.get("profile_pic_url_hd"),
            "external_url": data.get("external_url"),
            "is_private": data.get("is_private"),
            "account_type": "Business" if data.get("is_business") else "Personal",
            "posts": posts,
            "status": "success"
        }
    except requests.exceptions.RequestException as e:
        return {
            "username": username,
            "error": True,
            "status_code": getattr(e.response, 'status_code', None),
            "message": str(e),
            "status": "failed"
        }
