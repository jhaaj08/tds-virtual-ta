import re
import json

def extract_image_links(text):
    """
    Extracts image URLs from Markdown text, handling multiline URLs and hyphen line-breaks.
    Finds both standalone image links (![alt](url)) and images wrapped in links
    ([![alt](url)](url2 "title")).
    Returns a list of unique, cleaned URLs.
    """
    # Patterns allow for multiline content inside parentheses
    inner_pattern = r'!\[[^\]]*\]\(\s*([\s\S]+?)(?:\s+"[^"]*")?\s*\)'
    outer_pattern = r'\[!\[[^\]]*\]\([\s\S]*?\)\]\(\s*([\s\S]+?)(?:\s+"[^"]*")?\s*\)'
    
    # Find all matches with DOTALL to include newlines
    inner_urls = re.findall(inner_pattern, text, flags=re.DOTALL)
    outer_urls = re.findall(outer_pattern, text, flags=re.DOTALL)
    
    # Combine, clean (remove newlines/spaces), and dedupe
    all_urls = inner_urls + outer_urls
    cleaned = []
    for url in all_urls:
        u = url.strip().replace('\n', '').replace('\r', '')
        if u not in cleaned:
            cleaned.append(u)
    return cleaned

def extract_image_links_from_file(file_path):
    """
    Reads the given Markdown file and extracts all image URLs using extract_image_links().
    Raises FileNotFoundError if the path is invalid.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return extract_image_links(content)

if __name__ == "__main__":
    md_path = 'data/threads/thread_12345.md'
    output_json = 'data/image_links.json'
    try:
        links = extract_image_links_from_file(md_path)
        # Prepare data structure
        data = {'image_urls': links}
        # Write to JSON file
        with open(output_json, 'w', encoding='utf-8') as jf:
            json.dump(data, jf, ensure_ascii=False, indent=2)
        print(f"Extracted {len(links)} image URLs and saved to {output_json}")
    except FileNotFoundError:
        print(f"Error: File not found: {md_path}")
