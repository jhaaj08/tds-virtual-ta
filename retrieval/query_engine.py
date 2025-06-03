# retrieval/query_engine.py

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

model = SentenceTransformer("all-MiniLM-L6-v2")  # or whatever you used earlier

client = chromadb.PersistentClient(path="db")
collection = client.get_or_create_collection("tds_content")

def get_top_chunks(question, k=5):
    query_embedding = model.encode([question]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=k)
    
    # You can choose to return just content or (content + metadata)
    return results["documents"][0]  # list of top-k chunks