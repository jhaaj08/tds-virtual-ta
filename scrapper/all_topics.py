import os
import requests
import json
from dotenv import load_dotenv

# Load cookie from .env
load_dotenv()
Current_Cookie = "TMBB38kEwii8KwRhJhckvJ5UUK8geJ5BuPpwRqi5soyGKuxS%2F1BRxekvxT%2FGMZheHih68rbg5QMEcuqctspHOEGhdXngXsjaWzXN4O9W44mPWo933DVxNIml3PEyxq3Q0ccdBRLnGKeyPe2ITIEW2HX2yKKvlfRbq6JhvUSchwqNbru09AvLHkbK2JALplaA5IFNyCNzRri33K5DgulmbBwBwANVCF2y3Eu%2B%2BbfVk%2FGxlnkyUlqU4yFO%2BPmd9t4py99M4uYmzzGrQOSevIleIVUZRftiMBpTBarehGlpVLJzc8VyT0bJkQ%3D%3D--9XmOl74QjSsexn4U--D6YW3L8l39H1KPa3r6IlRA%3D%3D"

# Constants
BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY_SLUG = "courses/tds-kb"
CATEGORY_ID = 34

# Requests session
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Cookie": f"_t={Current_Cookie}"
})

def update_cookie_from_response(response):
    global Current_Cookie
    if "set-cookie" in response.headers:
        cookies = response.headers["set-cookie"]
        for part in cookies.split(";"):
            if "_t=" in part:
                Current_Cookie = part.strip().split("_t=")[-1]
                session.headers.update({"Cookie": f"_t={Current_Cookie}"})
                print("🔄 Updated cookie from response.")
                break

def fetch_all_topics():
    print("🔎 Fetching all topics...")
    page = 0
    all_topics = []

    while True:
        url = f"{BASE_URL}/c/{CATEGORY_SLUG}/{CATEGORY_ID}.json?page={page}"
        print(url)
        response = session.get(url)
        update_cookie_from_response(response)

        if response.status_code != 200:
            print(f"❌ Failed at page {page}: Status {response.status_code}")
            break

        data = response.json()
        topic_list = data.get("topic_list", {}).get("topics", [])
        if not topic_list:
            break

        for topic in topic_list:
            all_topics.append({
                "id": topic["id"],
                "slug": topic["slug"],
                "url": f"{BASE_URL}/t/{topic['slug']}/{topic['id']}"
            })

        print(f"📄 Page {page}: {len(topic_list)} topics")
        page += 1

    print(f"\n✅ Total topics fetched: {len(all_topics)}")
    return all_topics

def save_topics(topics, path="data/all_topics.json"):
    os.makedirs("data", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(topics, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved all topics to {path}")

if __name__ == "__main__":
    topics = fetch_all_topics()
    save_topics(topics)