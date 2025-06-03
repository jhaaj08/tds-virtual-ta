import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from tqdm import tqdm
import json
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
DISCOURSE_COOKIE = os.getenv("DISCOURSE_COOKIE")

# Setup session with just the _t cookie
session = requests.Session()
session.cookies.set("_t", DISCOURSE_COOKIE, domain="discourse.onlinedegree.iitm.ac.in")
session.headers.update({"User-Agent": "Mozilla/5.0"})

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY_SLUG = "courses/tds-kb"
CATEGORY_ID = 34

# Date range
START_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime(2025, 4, 14, tzinfo=timezone.utc)

def get_topic_ids():
    topics = []
    for page in tqdm(range(0, 30), desc="📄 Fetching topic pages"):
        url = f"{BASE_URL}/c/{CATEGORY_SLUG}/{CATEGORY_ID}.json?page={page}"
        r = session.get(url)
        if r.status_code != 200:
            print(f"❌ Failed to fetch page {page}, status: {r.status_code}")
            break
        data = r.json()
        new_topics = data.get("topic_list", {}).get("topics", [])
        if not new_topics:
            break
        topics.extend(new_topics)
    return topics

def get_posts_in_topic(topic_id):
    r = session.get(f"{BASE_URL}/t/{topic_id}.json")
    if r.status_code != 200:
        print(f"⚠️ Could not fetch topic {topic_id}")
        return []
    data = r.json()
    return [
        {
            "username": post["username"],
            "created_at": post["created_at"],
            "content": BeautifulSoup(post["cooked"], "html.parser").get_text(),
            "post_url": f"{BASE_URL}/t/{topic_id}/{post['post_number']}"
        }
        for post in data.get("post_stream", {}).get("posts", [])
    ]

def main():
    all_posts = []
    topics = get_topic_ids()

    for topic in tqdm(topics, desc="📬 Processing topics"):
        created_at = datetime.fromisoformat(topic["created_at"].replace("Z", "+00:00"))
        if START_DATE <= created_at <= END_DATE:
            topic_id = topic["id"]
            posts = get_posts_in_topic(topic_id)
            all_posts.extend(posts)

    os.makedirs("data", exist_ok=True)
    with open("data/discourse_posts.jsonl", "w", encoding="utf-8") as f:
        for post in all_posts:
            f.write(json.dumps(post, ensure_ascii=False) + "\n")

    print(f"\n✅ Scraped {len(all_posts)} posts and saved to data/discourse_posts.jsonl")

if __name__ == "__main__":
    main()