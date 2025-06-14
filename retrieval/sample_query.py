import numpy as np
import os 
import sys
from pathlib import Path

#Add project root to sys.path so `llm` is discoverable
sys.path.append(str(Path(__file__).resolve().parents[1]))

from llm.llm_client import LLMClient

base_url = os.getenv("OPENAI_BASE_URL")
api_key = os.getenv("OPENAI_API_KEY")
query = "If a student scores 10/10 on GA4 as well as a bonus, how would it appear on the dashboard?"
llm = LLMClient(base_url=base_url, api_key=api_key, model="gpt-4o-mini")
query_embedding = llm.get_embedding(query)

# Load archive
data = np.load("data/embeddings/sample_embed.npz", allow_pickle=True)
chunks = data["chunks"]
embeddings = data["embeddings"]

# Compute cosine similarities
from numpy.linalg import norm

def cosine_sim(a, b):
    return np.dot(a, b) / (norm(a) * norm(b))

scores = [cosine_sim(query_embedding, emb) for emb in embeddings]
top_idx = sorted(range(len(scores)), key=lambda i: -scores[i])[:3]

# Print top chunks
print("\n🔍 Top Matches:")
for i in top_idx:
    print(f"\n➡️ Chunk {i} (score: {scores[i]:.4f}):\n{chunks[i]}")