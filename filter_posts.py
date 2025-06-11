import json
from datetime import datetime, timezone

# Date range
START_DATE = datetime(2025, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime(2025, 4, 14, tzinfo=timezone.utc)

input_path = "data/discourse_posts.jsonl"
output_path = "data/discourse_posts_filtered.jsonl"

with open(input_path, "r", encoding="utf-8") as infile, open(output_path, "w", encoding="utf-8") as outfile:
    count = 0
    for line in infile:
        post = json.loads(line)
        created_at = datetime.fromisoformat(post["created_at"].replace("Z", "+00:00"))
        if START_DATE <= created_at <= END_DATE:
            outfile.write(json.dumps(post, ensure_ascii=False) + "\n")
            count += 1

print(f"✅ Filtered {count} posts and saved to {output_path}")