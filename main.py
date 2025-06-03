# api/main.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
from retrieval.query_engine import get_top_chunks  # you'll write this
from llm.response_generator import generate_answer  # you'll write this
from dotenv import load_dotenv
import base64
import os

load_dotenv()

app = FastAPI()

class Query(BaseModel):
    question: str
    image: str | None = None  # base64 image string (optional)

@app.post("/api/")
async def answer_question(query: Query):
    # 1. Step: Get top relevant chunks from ChromaDB
    top_chunks = get_top_chunks(query.question, k=5)

    # 2. Step: Pass question + context to LLM
    answer, links = generate_answer(query.question, top_chunks)

    return {
        "answer": answer,
        "links": links
    }