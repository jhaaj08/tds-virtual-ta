import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="db")
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

collection = client.get_or_create_collection("tds_virtual_ta", embedding_function=embedding_fn)

def get_relevant_chunks(query, k=5):
    results = collection.query(query_texts=[query], n_results=k)
    return results["documents"][0], results["metadatas"][0]

if __name__ == "__main__":
    question = input("❓ Enter your question: ")
    docs, metas = get_relevant_chunks(question)
    for i in range(len(docs)):
        print(f"\n--- Result {i+1} ---")
        print(docs[i])
        print(metas[i])