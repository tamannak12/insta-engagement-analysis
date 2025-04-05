import sys
import os
import json
from dotenv import load_dotenv

# Add project root to path to fix imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(project_root)

# Load environment variables
load_dotenv()

from src.scraper.fetch_data import fetch_instagram_data
from src.scraper.save_to_db import save_profile, save_posts, save_comments
from src.config.db import get_db  # MongoDB connection

def main():
    """Main function to fetch Instagram data including comments."""
    usernames = ["taylorswift", "zuck", "cristiano"]

    db = get_db()  # MongoDB connection
    if db is None:  # ✅ Explicitly check if db is None
        print("❌ Failed to connect to MongoDB. Exiting.")
        return

    try:
        for username in usernames:
            print(f"📌 Fetching data for {username}...")
            data = fetch_instagram_data(username)

            if data["status"] == "success":
                print(f"✅ Profile data fetched for {username}")
                print(f"✅ {len(data['posts'])} posts fetched for {username}")

                if len(data["posts"]) > 0:
                    print("📝 Sample post data:", data["posts"][0])  # Debugging

                # Save profile and posts
                save_profile(data)
                save_posts(data["username"], data["posts"])

                # Save comments separately
                for post in data["posts"]:
                    save_comments(post["id"], post["comments"])

                print(f"✅ Data successfully saved for {username}\n")
            else:
                print(f"❌ Failed to fetch {username}: {data.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    main()
