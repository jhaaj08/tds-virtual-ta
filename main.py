from fastapi import FastAPI
from pydantic import BaseModel
import base64
from PIL import Image
import io
import pytesseract
from dotenv import load_dotenv
from pathlib import Path
import os

from retrieval.query_engine import get_top_chunks
from llm.llm_client import LLMClient
from llm.response_generator import generate_answer

load_dotenv()

app = FastAPI()

class Query(BaseModel):
    question: str
    image: str | None = None  # Optional image


def extract_text_from_image(image_str: str | None) -> str:
    """Extract text using OCR from base64 or file:// input. Fail silently on errors."""
    if not image_str:
        return ""

    try:
        if image_str.startswith("file://"):
            filepath = image_str.replace("file://", "")
            if not os.path.isabs(filepath):
                filepath = str(Path(__file__).parent / filepath)
            with open(filepath, "rb") as f:
                image_data = f.read()
        else:
            image_data = base64.b64decode(image_str)

        image = Image.open(io.BytesIO(image_data))
        return pytesseract.image_to_string(image).strip()

    except Exception as e:
        print(f"[Warning] OCR skipped due to error: {e}")
        return ""


@app.post("/api/")
async def answer_question(query: Query):
    image_text = extract_text_from_image(query.image)
    combined_input = f"{query.question}\n{image_text}" if image_text else query.question

    top_chunks = get_top_chunks(combined_input)
    print(top_chunks)
    answer, links = generate_answer(query.question, top_chunks)

    return {"answer": answer, "links": links}

