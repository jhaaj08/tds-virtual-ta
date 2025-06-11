import requests, os, json, time
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from tqdm import tqdm

START_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime(2025, 4, 14, tzinfo=timezone.utc)
BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
TOPICS_FILE = "data/all_topics.json"
LOG_FILE = "data/scrape_log.json"
OUTPUT_FILE = "data/discourse_filtered_posts.jsonl"

# Initial Cookie (only needed for first request)
CURRENT_COOKIE = "bmz3zK5oGQqzVsGfl%2FmWUrFP%2BdbX%2F7NvZCuhDUk0tyEWgn28ROxe72AWB2pTuU1Uk8SQlAbI%2B7tylijSg604%2B%2BhjsdpRC6hhgbOXuUWJpXw0lN0ZaeywGDAStDjPYZKS3cQLV3uaA36gAuGU%2BMYriecyTiO2fHdvdrK8%2FPQWWMf01OJ2ku7TWZ5IuSF%2BDy5kZ%2Fesw5GLiEVrkVS1N2CIqJpHQHlXaGEuRBXWrFFOTk%2Bv%2F4citpNejiG4%2FkOXjcObb3krSY3zRNjhTR9ThZovmQ60x1XJ6E9cURIHNN644GvKvIQBZPoUlQ%3D%3D--e4xR2qqJS9uG3%2BNT--WYgTfOHN0cbgH%2F45RQgqkg%3D%3D"

# Load already-scraped log
scrape_log = json.load(open(LOG_FILE)) if os.path.exists(LOG_FILE) else {}

# Load topic list
topics = json.load(open(TOPICS_FILE))

def update_cookie_from_response(resp):
    global CURRENT_COOKIE
    for cookie in resp.cookies:
        if cookie.name == "_t":
            CURRENT_COOKIE = cookie.value

def get_post_ids(topic_id, slug):
    url = f"{BASE_URL}/t/{slug}/{topic_id}.json"
    headers = {"Cookie": f"_t={CURRENT_COOKIE}"}
    r = requests.get(url, headers=headers)
    update_cookie_from_response(r)
    if r.status_code != 200:
        raise Exception(f"Failed to get topic: {r.status_code}")
    return r.json()["post_stream"]["stream"]

def fetch_post(post_id, topic_id, slug):
    url = f"{BASE_URL}/posts/{post_id}.json"
    headers = {"Cookie": f"_t={CURRENT_COOKIE}"}
    r = requests.get(url, headers=headers)
    update_cookie_from_response(r)
    if r.status_code != 200:
        return None
    post = r.json()
    created_at = datetime.fromisoformat(post["created_at"].replace("Z", "+00:00"))
    if START_DATE <= created_at <= END_DATE:
        return {
            "username": post["username"],
            "created_at": post["created_at"],
            "content": BeautifulSoup(post["cooked"], "html.parser").get_text(),
            "post_url": f"{BASE_URL}/t/{slug}/{post['post_number']}"
        }

def append_posts(posts):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        for post in posts:
            f.write(json.dumps(post, ensure_ascii=False) + "\n")

def save_log():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(scrape_log, f, indent=2)

# Main Scraping Loop
for topic in tqdm(topics, desc="Scraping topics"):
    tid = str(topic["id"])
    slug = topic["slug"]
    if tid in scrape_log:
        continue

    try:
        post_ids = get_post_ids(tid, slug)
        filtered = []
        for pid in post_ids:
            try:
                post = fetch_post(pid, tid, slug)
                if post:
                    filtered.append(post)
                time.sleep(0.2)
            except:
                continue
        append_posts(filtered)
        scrape_log[tid] = {
            "slug": slug,
            "filtered_post_count": len(filtered),
            "status": "success"
        }
    except Exception as e:
        scrape_log[tid] = {
            "slug": slug,
            "filtered_post_count": 0,
            "status": "error",
            "error": str(e)
        }

    save_log()