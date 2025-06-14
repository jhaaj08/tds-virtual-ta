import os
import json
import re
import requests
import base64
from pathlib import Path
import sys

# Add root to sys.path to allow llm module import
sys.path.append(str(Path(__file__).resolve().parents[1]))
from llm.llm_gemini import get_image_description  # your Gemini description function

# ---- Paths ----
MARKDOWN_PATH = Path("data/threads/thread_12345.md")
OUTPUT_PATH = Path("data/threads/thread_12345_described.md")
IMAGES_JSON = Path("data/image_links.json")
IMAGE_DIR = Path("data/images")
IMAGE_DIR.mkdir(exist_ok=True)

# ---- Load image links ----
with open(IMAGES_JSON, "r", encoding="utf-8") as f:
    image_data = json.load(f)
    image_urls = image_data.get("image_urls", [])

print(f"🔢 Total image URLs to process: {len(image_urls)}")

# ---- Download + Describe ----
def download_image(url: str) -> Path | None:
    try:
        filename = url.split("/")[-1].split("?")[0]
        local_path = IMAGE_DIR / filename
        if local_path.exists():
            return local_path
        response = requests.get(url)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(response.content)
        return local_path
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
        return None

# ---- Process Markdown ----
markdown = MARKDOWN_PATH.read_text(encoding="utf-8")

def inject_descriptions(markdown_text: str, image_urls: list[str]) -> str:
    updated = markdown_text
    success_count = 0
    fail_count = 0

    for url in image_urls:
        url_clean = url.strip().replace("\n", "")
        pattern = re.escape(url_clean)
        match = re.search(pattern, updated)
        if match:
            image_path = download_image(url_clean)
            if not image_path:
                fail_count += 1
                continue

            description = get_image_description(str(image_path)).strip()
            inject_text = f"\n> 📝 Image description: {description}\n"
            updated = updated[:match.end()] + inject_text + updated[match.end():]
            success_count += 1
        else:
            print(f"⚠️ Image URL not found in markdown: {url_clean}")
            fail_count += 1

    print(f"✅ Described {success_count} images")
    print(f"⚠️ Failed or skipped: {fail_count}")
    return updated

# ---- Save updated markdown ----
described_text = inject_descriptions(markdown, image_urls)
OUTPUT_PATH.write_text(described_text, encoding="utf-8")
print(f"📄 Updated markdown with descriptions saved to: {OUTPUT_PATH}")