from pathlib import Path

INPUT_DIR = Path(__file__).resolve().parents[1] / "tools-in-data-science-public"
OUTPUT_FILE = Path(__file__).resolve().parents[1] / "data/course_content.txt"

def merge_markdown_files():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for md_file in sorted(INPUT_DIR.glob("*.md")):
            out.write(f"# {md_file.stem.replace('-', ' ').title()}\n\n")
            content = md_file.read_text(encoding="utf-8")
            out.write(content + "\n\n")

    print(f"✅ Extracted course content into {OUTPUT_FILE}")

if __name__ == "__main__":
    merge_markdown_files()