import json
import os
import sys
from pathlib import Path
import time
from tqdm import tqdm


# Add project root to sys.path so `llm` is discoverable
sys.path.append(str(Path(__file__).resolve().parents[1]))

from llm.llm_client import LLMClient
import chromadb
from chromadb.config import Settings

# --- Custom embedding wrapper ---
class CustomEmbeddingFunction:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def __call__(self, input: list[str]) -> list[list[float]]:
        return self.llm_client.get_embedding(input, embed_model="text-embedding-3-small")

    def name(self):
        return "custom-llm-embedding"
    
# --- Paths ---
COURSE_FILE = Path("data/course_content.txt")
DISCOURSE_FILE = Path("data/discourse_filtered_posts.jsonl")

# --- LLM setup ---
API_BASE_URL = os.getenv("OPENAI_BASE_URL")
print(API_BASE_URL)
API_KEY = os.getenv("AIPROXY_TOKEN")
print(API_KEY)
MODEL = "text-embedding-3-small"
llm_client = LLMClient(base_url=API_BASE_URL, api_key=API_KEY, model=MODEL)

# --- ChromaDB setup ---
chroma_client = chromadb.PersistentClient(path="db")
embedding_fn = CustomEmbeddingFunction(llm_client)
collection = chroma_client.get_or_create_collection("tds_virtual_ta", embedding_function=embedding_fn)

# --- Utility: text splitting ---
def split_text(text, chunk_size=500):
    paragraphs = text.split("\n")
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) < chunk_size:
            current += p + "\n"
        else:
            chunks.append(current.strip())
            current = p + "\n"
    if current:
        chunks.append(current.strip())
    return chunks

# --- Embedding functions ---
def embed_course_content():
    text = COURSE_FILE.read_text(encoding="utf-8")
    chunks = split_text(text)
    print(f"🔹 Total course chunks: {len(chunks)}")
    
    for i, chunk in enumerate(tqdm(chunks, desc="Embedding course content")):
        doc_id = f"course-{i}"
        try:
            collection.add(
                documents=[chunk],
                metadatas=[{"source": "course"}],
                ids=[doc_id]
            )
        except chromadb.errors.IDAlreadyExistsError:
            continue  # Skip if already embedded
        except Exception as e:
            print(f"⚠️ Failed on {doc_id}: {e}")
            time.sleep(5)  # Backoff on error

def embed_discourse_posts():
    with open(DISCOURSE_FILE, encoding="utf-8") as f:
        lines = f.readlines()

    print(f"🔹 Total Discourse posts: {len(lines)}")

    for i, line in enumerate(tqdm(lines, desc="Embedding discourse posts")):
        doc_id = f"discourse-{i}"
        try:
            post = json.loads(line)
            doc = post["content"]
            collection.add(
                documents=[doc],
                metadatas=[{
                    "source": "discourse",
                    "url": post.get("post_url"),
                    "author": post.get("username"),
                    "created_at": post.get("created_at")
                }],
                ids=[doc_id]
            )
        except chromadb.errors.IDAlreadyExistsError:
            continue  # Already embedded
        except Exception as e:
            print(f"⚠️ Failed on {doc_id}: {e}")
            time.sleep(5)

# --- Entry point ---
if __name__ == "__main__":
    embed_course_content()
    embed_discourse_posts()
    print("✅ Embeddings stored in ChromaDB (db/ folder)")