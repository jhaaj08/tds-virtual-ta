import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Paths
COURSE_FILE = Path("data/course_content.txt")
DISCOURSE_FILE = Path("data/discourse_posts.jsonl")

# Chroma DB setup
client = chromadb.PersistentClient(path="db")
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

collection = client.get_or_create_collection("tds_virtual_ta", embedding_function=embedding_fn)

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

def embed_course_content():
    text = COURSE_FILE.read_text(encoding="utf-8")
    chunks = split_text(text)
    for i, chunk in enumerate(chunks):
        collection.add(documents=[chunk], metadatas=[{"source": "course"}], ids=[f"course-{i}"])

def embed_discourse_posts():
    with open(DISCOURSE_FILE, encoding="utf-8") as f:
        for i, line in enumerate(f):
            post = json.loads(line)
            doc = post["content"]
            collection.add(documents=[doc], metadatas=[{
                "source": "discourse",
                "url": post.get("post_url"),
                "author": post.get("username"),
                "created_at": post.get("created_at")
            }], ids=[f"discourse-{i}"])

if __name__ == "__main__":
    embed_course_content()
    embed_discourse_posts()
    print("✅ Embeddings stored in ChromaDB (db/ folder)")