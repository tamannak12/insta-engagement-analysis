import sys
import os
from dotenv import load_dotenv
from tabulate import tabulate
import textwrap

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Load environment variables
load_dotenv()

from src.database.queries import (
    get_profile_by_username,
    get_all_profiles,
    search_profiles,
    get_posts_by_username
)

def display_profile(profile):
    """Display profile information and posts in a tabulated format."""
    if not profile:
        print("\nProfile not found.\n")
        return

    print("\n" + "=" * 80)
    print(f" Instagram Profile: {profile['username']} ")
    print("=" * 80)

    profile_table = [
        ["Username", profile.get("username", "N/A")],
        ["Full Name", profile.get("full_name", "N/A")],
        ["Followers", f"{profile.get('follower_count', 0):,}"],
        ["Following", f"{profile.get('following_count', 0):,}"],
        ["Posts", f"{profile.get('media_count', 0):,}"],
        ["Verified", "✓" if profile.get("is_verified", False) else "✗"],
        ["Account Type", profile.get("account_type", "N/A")],
        ["Private", "Yes" if profile.get("is_private", False) else "No"],
    ]
    print(tabulate(profile_table, tablefmt="fancy_grid"))

    if profile.get("biography"):
        print("\n📜 Bio:\n" + profile["biography"])

    if "bio_links" in profile and profile["bio_links"]:
        bio_links_table = [[link.get("title", "Link"), link.get("url", "N/A")] for link in profile["bio_links"]]
        print("\n🔗 Bio Links:")
        print(tabulate(bio_links_table, headers=["Title", "URL"], tablefmt="fancy_grid"))

    # Fetch posts
    posts = get_posts_by_username(profile["username"], limit=15)
    if posts:
        print("\n🖼️ Recent Posts:")
        for post in posts:
            print(f"\n📌 Post ID: {post.get('_id', 'N/A')} (Likes: {post.get('like_count', 0):,}, Comments: {post.get('comment_count', 0):,})")

            # Format caption with proper wrapping
            if post.get('caption'):
                wrapped_caption = textwrap.fill(post['caption'], width=80)
                print(f"📝 Caption: {wrapped_caption}")
            else:
                print("📝 Caption: [No caption]")

            print("📆 Timestamp:", post.get("timestamp", "N/A"))

            # Display comments in table format if available
            if post.get("comments"):
                print("\n💬 Comments:")
                comments_table = [[comment.get("user", "Unknown"), textwrap.fill(comment.get("text", ""), width=60)] for comment in post["comments"]]
                print(tabulate(comments_table, headers=["Username", "Comment"], tablefmt="fancy_grid"))
            else:
                print("\n💬 No comments")

            print("-" * 80)

    print("=" * 80 + "\n")


def main():
    """Main function demonstrating different ways to fetch data."""
    usernames = ["taylorswift", "zuck", "cristiano"]

    for username in usernames:
        print(f"\n1️⃣ Fetching profile: {username}")
        profile = get_profile_by_username(username)
        display_profile(profile)

    print("\n2️⃣ Fetching all profiles (no limit):")
    profiles = get_all_profiles(limit=15)
    profile_table = [[p["username"], p["follower_count"], p["following_count"], p["media_count"]] for p in profiles]
    print(tabulate(profile_table, headers=["Username", "Followers", "Following", "Posts"], tablefmt="fancy_grid"))

    print("\n3️⃣ Searching for profiles:")
    search_term = "taylor"
    search_results = search_profiles(search_term)
    if search_results:
        search_table = [[p["username"], p["full_name"], p["follower_count"]] for p in search_results]
        print(tabulate(search_table, headers=["Username", "Full Name", "Followers"], tablefmt="fancy_grid"))
    else:
        print("No matching profiles found.")

if __name__ == "__main__":
    main()
