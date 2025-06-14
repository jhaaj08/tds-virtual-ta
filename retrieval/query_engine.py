# retrieval/query_engine.py
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os 

from dotenv import load_dotenv
load_dotenv()

# 👇 Use a directory inside your project folder
persist_dir = os.path.join(os.getcwd(), "db")

# ✅ Use the same embedding model you used during embedding
embedding_model = "text-embedding-3-small"
embeddings = OpenAIEmbeddings(model=embedding_model)

# ✅ Initialize the Chroma DB
db = Chroma(
    persist_directory=persist_dir,
    embedding_function=embeddings,
)

# ✅ Create retriever
retriever = db.as_retriever(search_kwargs={"k": 5})

# ✅ Core function to get top chunks for a query
def get_top_chunks(query: str):
    docs = retriever.invoke(query)

    top_chunks = []
    for doc in docs:
        top_chunks.append({
            "content": doc.page_content,
            "metadata": doc.metadata
        })

    return top_chunks