import tweepy
import json
import os
import time
from dotenv import load_dotenv
from pprint import pprint
from pymongo import MongoClient, errors as pymongo_errors
import traceback
from datetime import datetime

# --- Configuration ---

# Load environment variables from .env file
load_dotenv()

# Get the Bearer Token from environment variables
# --- THIS MUST BE THE BEARER TOKEN FROM YOUR TWITTER DEVELOPER PORTAL APP ---
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
if not BEARER_TOKEN:
    raise ValueError("Bearer Token not found. Please set the BEARER_TOKEN environment variable in your .env file (obtain from developer.twitter.com).")

# --- Parameters for Data Fetching ---
# The numeric User ID of the X account you want to fetch tweets from
# Example: TwitterDev (2244994945), XEng (17919972)
# Check API access level requirements for the user/endpoint.
USER_ID_TO_SCRAPE = "17919972"  # Example: XEng User ID. <--- REPLACE WITH TARGET USER ID

# Maximum TOTAL number of tweets you want to fetch (across multiple API calls)
# KEEP THIS VERY LOW (e.g., 10, 50, 100 MAX) TO AVOID HITTING FREE TIER LIMITS INSTANTLY.
# As of April 2025, free tier limits are extremely restrictive.
MAX_TWEETS_TO_FETCH = 10 # Be extremely mindful of API limits!

# Tweets per API request (pagination page size). Max 100 for user timelines endpoint.
# Min value is 5 for v2 user tweets endpoint.
RESULTS_PER_PAGE = min(MAX_TWEETS_TO_FETCH, 10) # Fetch fewer per page if max_tweets is low

# Specify which tweet fields you want (match API v2 names)
# Reference: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
TWEET_FIELDS = [
    "created_at", "public_metrics", "author_id", "conversation_id",
    "in_reply_to_user_id", "lang", "source", "referenced_tweets",
    "attachments", "entities",
    # Add more fields as needed: "geo", "context_annotations", etc.
    # Check if your API access level permits requested fields.
]

# Use expansions to get related objects (match API v2 names)
# Reference: https://developer.twitter.com/en/docs/twitter-api/expansions
EXPANSIONS = [
    "author_id", "attachments.media_keys", "referenced_tweets.id",
    "referenced_tweets.id.author_id", "in_reply_to_user_id",
]

# Specify fields for the expanded objects (match API v2 names)
# Reference: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user
USER_FIELDS = ["username", "name", "profile_image_url", "verified", "public_metrics"]
# Reference: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/media
MEDIA_FIELDS = ["media_key", "type", "url", "preview_image_url", "public_metrics", "duration_ms", "alt_text"]


# --- API Interaction & Data Processing ---

def fetch_tweets_with_api_v2(bearer_token, user_id, max_tweets, results_per_page,
                              tweet_fields, expansions, user_fields, media_fields):
    """
    Fetches tweets for a user ID using Tweepy and the Twitter API v2,
    handles pagination, rate limits gracefully (within reason), manages common API errors,
    uses expansions, and structures data.
    """
    # Initialize Tweepy Client with Bearer Token
    # wait_on_rate_limit=True tells Tweepy to automatically wait if rate limited (HTTP 429)
    # NOTE: This might not save you from monthly quota limits, only short-term rate limits.
    print("[*] Initializing Tweepy Client...")
    try:
        client = tweepy.Client(bearer_token, wait_on_rate_limit=True)
        # Verify authentication works by fetching basic user info (consumes API call)
        print("[*] Verifying authentication...")
        client.get_user(id=user_id)
        print("[+] Authentication successful.")
    except tweepy.errors.TweepyException as e:
        print(f"[!] Error initializing Tweepy client or authenticating: {e}")
        print("[!] Check your Bearer Token and API access level.")
        return []
    except Exception as e:
        print(f"[!] An unexpected error occurred during client initialization: {e}")
        return []

    tweets_data_for_db = []
    fetched_tweets_count = 0 # Keep track for logging

    # Ensure results_per_page is valid (5-100 for this endpoint)
    valid_results_per_page = max(5, min(100, results_per_page))

    print(f"[*] Starting fetch for user ID: {user_id}. Target: {max_tweets} tweets.")
    print(f"[*] Tweets per API page request: {valid_results_per_page}")
    print("[!] WARNING: Free API tier limits are very strict. Fetch may stop early.")

    # Use Tweepy's Paginator for easy handling of multiple pages
    # The Paginator's 'limit' parameter controls the TOTAL number of items (tweets) to return.
    paginator = tweepy.Paginator(
        client.get_users_tweets,
        id=user_id,
        max_results=valid_results_per_page,
        tweet_fields=tweet_fields,
        expansions=expansions,
        user_fields=user_fields,
        media_fields=media_fields,
        limit=max_tweets  # <-- CORRECTED: Let Paginator handle the total tweet limit
    )

    try:
        page_count = 0
        # The Paginator will stop yielding responses once 'limit' (max_tweets) is reached
        # or there are no more tweets from the API.
        for response in paginator:
            page_count += 1
            print(f"[*] Processing page {page_count}...")

            # --- Log API Errors/Warnings ---
            if response.errors:
                print(f"[!] API Errors/Warnings on page {page_count}:")
                for error in response.errors:
                    print(f"  - {error}")
                    # Handle specific errors if needed

            # --- Safely Prepare Included Data Lookups ---
            includes = response.includes if response.includes else {}
            users = {user.id: user for user in includes.get('users', [])}
            media = {m.media_key: m for m in includes.get('media', [])}
            referenced_tweets_lookup = {tweet.id: tweet for tweet in includes.get('tweets', [])}

            # --- Process Main Tweet Data ---
            tweets_on_page = response.data if response.data else []
            if not tweets_on_page and not response.errors: # Check for empty page without errors
                print("  -> No tweet data found on this page (may be end of timeline or gap).")
                # Paginator should handle stopping, but we can log this.
                # If there were errors, they were logged above.

            # --- Structure Each Tweet on the Page ---
            for tweet in tweets_on_page:
                # No need for manual max_tweets check here, Paginator handles the limit.

                author_info = users.get(tweet.author_id)

                # Process attachments
                attachments_info = []
                if tweet.attachments and 'media_keys' in tweet.attachments:
                    for key in tweet.attachments['media_keys']:
                        medium = media.get(key)
                        if medium:
                            attachments_info.append(medium)

                # Process referenced tweets
                referenced_tweets_info = []
                if tweet.referenced_tweets:
                    for ref in tweet.referenced_tweets:
                        ref_tweet_details = referenced_tweets_lookup.get(ref.id)
                        ref_author_info = None
                        if ref_tweet_details:
                            ref_author_info = users.get(ref_tweet_details.author_id)

                        referenced_tweets_info.append({
                            "type": ref.type,
                            "id": str(ref.id), # Ensure string ID
                            "text": ref_tweet_details.text if ref_tweet_details else None,
                            "author_id": str(ref_tweet_details.author_id) if ref_tweet_details else None,
                            "author_username": ref_author_info.username if ref_author_info else None,
                            "error": "Referenced tweet details not found/included by API." if not ref_tweet_details else None
                        })

                # Construct the tweet document for storage
                tweet_doc = {
                    "_id": str(tweet.id), # Use tweet ID as MongoDB _id (ensure string)
                    "text": tweet.text,
                    "created_at": tweet.created_at,
                    "author_id": str(tweet.author_id), # Ensure string
                    "author_username": author_info.username if author_info else None,
                    "author_name": author_info.name if author_info else None,
                    "author_verified": author_info.verified if author_info else None,
                    "conversation_id": str(tweet.conversation_id), # Ensure string
                    "language": tweet.lang,
                    "source": tweet.source,
                    "public_metrics": tweet.public_metrics, # dict
                    "entities": tweet.entities, # dict (if requested)
                    "in_reply_to_user_id": str(tweet.in_reply_to_user_id) if tweet.in_reply_to_user_id else None, # Ensure string
                    "referenced_tweets": referenced_tweets_info or None,
                    "attachments": [
                        {
                            "media_key": medium.media_key,
                            "type": medium.type,
                            "url": getattr(medium, 'url', None),
                            "preview_image_url": getattr(medium, 'preview_image_url', None),
                            "public_metrics": getattr(medium, 'public_metrics', None),
                            "duration_ms": getattr(medium, 'duration_ms', None),
                            "alt_text": getattr(medium, 'alt_text', None),
                        } for medium in attachments_info
                    ] or None,
                }
                tweets_data_for_db.append(tweet_doc)
                fetched_tweets_count += 1 # Increment count for logging

            # --- End of processing tweets on the page ---
            print(f"  -> Collected {fetched_tweets_count} tweets so far.")
            # No need for outer break check based on count, Paginator handles stopping at its limit.

    except tweepy.errors.TweepyException as e:
        print(f"\n[!] Error during pagination/API request: {e}")
        # Provide more details if available from the exception
        if hasattr(e, 'api_codes'):
             print(f"  API Error Codes: {e.api_codes}")
        if hasattr(e, 'api_messages'):
             print(f"  API Error Messages: {e.api_messages}")
        if isinstance(e, tweepy.errors.Forbidden):
             print("[!] Received Forbidden (403). You may not have permission for this endpoint/user/field with your API access level.")
        if isinstance(e, tweepy.errors.TooManyRequests):
             print("[!] Received Too Many Requests (429). Tweepy's wait_on_rate_limit might not be enough, or you hit a non-hourly limit (like monthly quota).")
        # Add check for Unauthorized (401) - indicates token issue
        if isinstance(e, tweepy.errors.Unauthorized):
             print("[!] Received Unauthorized (401). Your Bearer Token is likely invalid or expired.")
    except Exception as e:
        print(f"\n[!] An unexpected error occurred: {e}")
        traceback.print_exc()

    print(f"\n[*] Finished fetching. Total tweets collected: {len(tweets_data_for_db)}")
    if len(tweets_data_for_db) < max_tweets:
         print("[!] Note: Fewer tweets collected than the target limit. This could be due to API monthly quota exhaustion, reaching the actual end of the user's timeline, or errors during the fetch.")
    return tweets_data_for_db

# --- Main Execution ---
if __name__ == "__main__":
    # Ensure prerequisites are met before running:
    # 1. Twitter Developer Account & Approved Project/App
    # 2. BEARER_TOKEN set in .env file
    # 3. Libraries installed: tweepy, python-dotenv, pymongo
    print(f"--- Starting Twitter API v2 Fetch ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    print(f"--- Target User ID: {USER_ID_TO_SCRAPE}, Max Tweets: {MAX_TWEETS_TO_FETCH} ---")

    scraped_data = fetch_tweets_with_api_v2(
        bearer_token=BEARER_TOKEN,
        user_id=USER_ID_TO_SCRAPE,
        max_tweets=MAX_TWEETS_TO_FETCH,
        results_per_page=RESULTS_PER_PAGE,
        tweet_fields=TWEET_FIELDS,
        expansions=EXPANSIONS,
        user_fields=USER_FIELDS,
        media_fields=MEDIA_FIELDS
    )

    if scraped_data:
        print(f"\n--- Sample Scraped Data (First {min(5, len(scraped_data))} Tweets) ---")
        pprint(scraped_data[:5])

        # Optional: Save the full 'scraped_data' list to a file
        output_filename = f"tweets_apiv2_{USER_ID_TO_SCRAPE}_{int(time.time())}.json"
        try:
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(scraped_data, f, ensure_ascii=False, indent=4, default=str) # Use default=str for datetime
            print(f"\n[*] Successfully saved {len(scraped_data)} tweets to {output_filename}")
        except Exception as e:
            print(f"\n[!] Error saving to JSON file ({output_filename}): {e}")

        # --- Storing in MongoDB Placeholder ---
        print("\n--- MongoDB Integration ---")
        try:
            # Ensure MONGO_URI and MONGO_DB_NAME are set in your .env file if not using defaults
            DB_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
            DB_NAME = os.getenv("MONGO_DB_NAME", "twitter_data")
            COLLECTION_NAME = f'user_{USER_ID_TO_SCRAPE}_apiv2' # Collection name specific to API v2

            if not DB_URI or not DB_NAME:
                 print("[!] MongoDB URI or DB_NAME not found in environment variables. Skipping DB insert.")
            else:
                mongo_client = MongoClient(DB_URI)
                db = mongo_client[DB_NAME]
                collection = db[COLLECTION_NAME]

                if scraped_data:
                    print(f"[*] Attempting to insert {len(scraped_data)} documents into MongoDB collection '{collection.name}'...")
                    try:
                        insert_result = collection.insert_many(scraped_data, ordered=False)
                        print(f"[*] Successfully inserted {len(insert_result.inserted_ids)} new documents.")
                    except pymongo_errors.BulkWriteError as bwe:
                        inserted_count = bwe.details.get('nInserted', 0)
                        duplicate_count = len(bwe.details.get('writeErrors', []))
                        print(f"[*] MongoDB BulkWriteError: Inserted: {inserted_count}, Duplicates ignored: {duplicate_count}")
                        if inserted_count == 0 and duplicate_count > 0:
                             print("[*] It seems all fetched tweets were already in the database.")
                else:
                    print("[*] No data to insert into MongoDB.")

                mongo_client.close()
                print("[*] MongoDB connection closed.")

        except ImportError:
            print("\n[!] pymongo not installed ('pip install pymongo'). Cannot store in MongoDB.")
        except pymongo_errors.ConnectionFailure as e:
             print(f"\n[!] Error connecting to MongoDB: {e}")
        except Exception as e:
            print(f"\n[!] Error storing data in MongoDB: {e}")
            traceback.print_exc()
    else:
        print("\n[!] No data was scraped. Check logs for API errors, limit issues, or connection problems.")

    print(f"--- Script finished ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")