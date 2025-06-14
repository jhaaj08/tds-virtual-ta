import os
import requests
from pathlib import Path
import re
import json
import html2text
from tqdm import tqdm

# — Configuration —
DISCOURSE_DOMAIN = "https://discourse.onlinedegree.iitm.ac.in"
TOPIC_ID = 165959
TOPIC_SLUG = "ga4-data-sourcing-discussion-thread-tds-jan-2025"
SESSION_COOKIE = "By1yc2iBae%2BYwP%2B4HSs8x4NQG6LiBPh5F4SNj16%2FB3JYI%2BX5B36tcFa9%2F1MJlZq6OuIz6XKvzhYzJnf1BwOHdts7BigRtDM2xAlS4pvz6MRnAizcVDnYEkJfxV2NaztlKeI%2BlHYHal1aFczABLrArXC%2FcH%2FZEOqfa9H5l1%2BjeeUMH3hbWWUMcgrZgCYcjiN9jOlFaWAvsS9%2BBR3r42%2F08drnlWX8%2Fi9tQ3II5LA%2F30XUcpW2eVwb1Epr%2FD8YSSB2l4xiRwjPg%2Bt6%2B3CGHjKfmRjrO%2Br28Ng7zsCTQp3adJLz86SLK0crbA%3D%3D--7lgIHB3nRpP5ulim--Ki%2FGtQGGS30rFt2QOhYLIw%3D%3D"

HEADERS = {
    "Cookie": f"_t={SESSION_COOKIE}"
}

# — Paths —
THREAD_DIR = Path("data/threads")
THREAD_DIR.mkdir(parents=True, exist_ok=True)
MARKDOWN_PATH = THREAD_DIR / f"thread_{TOPIC_ID}.md"
POST_IDS_PATH = THREAD_DIR / f"thread_{TOPIC_ID}_ids.json"

# — Helpers —
def fetch_json(url, params=None):
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()

def load_written_ids():
    if POST_IDS_PATH.exists():
        return set(json.loads(POST_IDS_PATH.read_text()))
    return set()

def save_written_ids(post_ids):
    POST_IDS_PATH.write_text(json.dumps(sorted(post_ids), indent=2))

def append_markdown(post_text):
    with open(MARKDOWN_PATH, "a", encoding="utf-8") as f:
        f.write(post_text + "\n\n")

def convert_post_to_markdown(post):
    author = post.get("username", "unknown")
    created = post.get("created_at", "")[:10]
    body_md = html2text.HTML2Text()
    body_md.ignore_links = False
    content = body_md.handle(post.get("cooked", "")).strip()
    return f"### {author} ({created})\n{content}"

# — Initial fetch —
topic_url = f"{DISCOURSE_DOMAIN}/t/{TOPIC_SLUG}/{TOPIC_ID}.json"
initial = fetch_json(topic_url)

total_posts = initial.get("posts_count", 0)
per_page = initial.get("post_stream", {}).get("posts_per_page", 20)
all_ids = initial.get("post_stream", {}).get("stream", [])
max_page = (total_posts + per_page - 1) // per_page
title = initial.get("title", "Untitled")

# Header markdown
if not MARKDOWN_PATH.exists():
    MARKDOWN_PATH.write_text(f"## Thread: {title}\n\n", encoding="utf-8")

written_ids = load_written_ids()
print(f"🔁 Resuming from {len(written_ids)} posts already saved")

new_ids = set()

# — Fetch page-by-page —
for page in tqdm(range(1, max_page + 1), desc="📥 Fetching pages"):
    page_url = f"{DISCOURSE_DOMAIN}/t/{TOPIC_SLUG}/{TOPIC_ID}/{page}.json"
    page_data = fetch_json(page_url)
    posts = page_data.get("post_stream", {}).get("posts", [])

    for post in posts:
        pid = post.get("id")
        if pid in written_ids or pid in new_ids:
            continue

        markdown = convert_post_to_markdown(post)
        append_markdown(markdown)
        new_ids.add(pid)

# — Finalize —
all_saved = written_ids.union(new_ids)
save_written_ids(all_saved)
print(f"✅ Total unique posts saved: {len(all_saved)} to {MARKDOWN_PATH}")