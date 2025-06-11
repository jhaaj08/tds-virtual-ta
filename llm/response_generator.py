# llm/response_generator.py

import os
from llm.llm_client import LLMClient
from dotenv import load_dotenv


API_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://aiproxy.sanand.workers.dev/openai/v1")
API_KEY = os.getenv("AIPROXY_TOKEN")  # AIPROXY_TOKEN
MODEL = "gpt-4o-mini"

print("LLMClient Initialized With API KEY:", repr(API_KEY))
client = LLMClient(base_url=API_BASE_URL, api_key=API_KEY, model=MODEL)


def generate_answer(question, top_chunks):
    # 1. Build context from top chunk contents
    context = "\n\n".join([chunk["content"] for chunk in top_chunks])

    # 2. Create prompt
    prompt = f"""You are a helpful assistant answering questions from IITM's Data Science Discourse forum.
Use the following context to answer the user's question.
If the answer is not in the context, say you don't know. Don't hallucinate.
Also, don't cite documents not in the context.

Question: {question}

Context:
{context}

Answer:"""

    # 3. Call LLM
    messages = [{"role": "user", "content": prompt}]
    response = client.chat(messages)

    # 4. Extract answer text
    answer = response["choices"][0]["message"]["content"]

    # 5. Build links from metadata
    links = []
    for chunk in top_chunks:
        meta = chunk.get("metadata", {})
        if meta.get("url") and meta.get("text"):
            links.append({
                "url": meta["url"],
                "text": meta["text"]
            })

    return answer, links