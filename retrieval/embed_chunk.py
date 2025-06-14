import json
import numpy as np
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter

import os
import sys
import tiktoken

# Add root to sys.path to allow llm module import
sys.path.append(str(Path(__file__).resolve().parents[1]))

from llm.llm_client import LLMClient  # Custom wrapper for get_embedding()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

# ---- Init LLM Client ----
client = LLMClient(
    base_url=base_url,
    api_key=api_key,
    model="gpt-4o-mini"
)
embed_model = "text-embedding-3-small"

enc = tiktoken.encoding_for_model(embed_model)
MAX_TOKENS = 8192

def is_within_token_limit(text, max_tokens=MAX_TOKENS):
    return len(enc.encode(text)) <= max_tokens

# --- Load ---
with open("data/sample_data.json", "r") as f:
    lines = f.readlines()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

all_chunks = []
all_embeddings = []

# --- Process Each Line ---
for line in lines:
    obj = json.loads(line)
    text = obj["content"]

    # Split into chunks
    chunks = splitter.split_text(text)

    # Filter by token length
    valid_chunks = [chunk for chunk in chunks if isinstance(chunk, str) and chunk.strip() and is_within_token_limit(chunk)]

    skipped = len(chunks) - len(valid_chunks)
    if skipped > 0:
        print(f"⚠️ Skipped {skipped} overlong chunks")

    if valid_chunks:
        embeddings = client.get_embedding(valid_chunks, embed_model=embed_model)
        all_chunks.extend(valid_chunks)
        all_embeddings.extend(embeddings)

# --- Save Output ---
np.savez_compressed(
    "data/embeddings/sample_embed.npz",
    embeddings=np.array(all_embeddings),
    chunks=np.array(all_chunks)
)

print(f"✅ Embedded {len(all_chunks)} chunks. Saved to data/embeddings/sample_embed.npz")