# llm/response_generator.py

# llm/response_generator.py
import os
from llm.llm_client import LLMClient
from dotenv import load_dotenv
import json


API_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://aiproxy.sanand.workers.dev/openai/v1")
API_KEY = os.getenv("AIPROXY_TOKEN")  # AIPROXY_TOKEN
MODEL = "gpt-4o-mini"

print("LLMClient Initialized With API KEY:", repr(API_KEY))
client = LLMClient(base_url=API_BASE_URL, api_key=API_KEY, model=MODEL)


def generate_answer(question, top_chunks):
    # 1. Build context from top chunk contents
    context = "\n\n".join([chunk["content"] for chunk in top_chunks])

    # 2. Create prompt
    prompt = f"""You are a helpful assistant answering student questions using the IITM Data Science Discourse forum archives.

    You must only use the context provided below to answer the question. Do not use prior knowledge or guess. If the answer is not clearly present in the context, reply: "I don’t know."

    When relevant, copy key phrases directly from the context. Do not paraphrase important details.

    Question:
    {question}

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
    for each_doc in top_chunks:
        meta = each_doc["metadata"]
        topic_url = meta.get("topic_url")
        post_data = json.loads(meta.get("post_data", "[]"))

        for each_post in post_data:
            obj = {
                "url": f"{topic_url}/{each_post['post_number']}",
                "text": each_post["content"]
            }
            links.append(obj)
    
    
    return answer, links