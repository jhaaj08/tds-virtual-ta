from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from llm.response_generator import generate_answer

# 1. Load the Chroma DB
db = Chroma(
    persist_directory="/Users/ajitjha/Downloads/db",  # Your DB path
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small")
)
print("✅ Chroma DB loaded")
print("✅ Collection count:", db._collection.count())

# 2. Create retriever
retriever = db.as_retriever(search_kwargs={"k": 5})

# 3. Your test question
query = "I know Docker but have not used Podman before. Should I use Docker for this course?"

# 4. Get top matching chunks
docs = retriever.invoke(query)

# 5. Convert LangChain docs to plain dicts for response generator
top_chunks = [{
    "content": doc.page_content,
    "metadata": doc.metadata
} for doc in docs]

# 6. Generate answer using your response generator
answer, links = generate_answer(query, top_chunks)

# 7. Output
print("\n🧠 Final Answer:\n", answer)
if links:
    print("\n🔗 Source Links:")
    for link in links:
        print(f"- {link['text']}: {link['url']}")