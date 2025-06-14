from fastapi import FastAPI, Request
from pydantic import BaseModel
import base64
from PIL import Image
import io
import pytesseract
from dotenv import load_dotenv
from pathlib import Path
import sys
from retrieval.query_engine import get_top_chunks
from llm.llm_client import LLMClient  # Custom wrapper for get_embedding()
from llm.response_generator import generate_answer
import os 

load_dotenv()  # place this early in main.py
app = FastAPI()

class Query(BaseModel):
    question: str
    image: str | None = None  # Optional image

def extract_text_from_image(image_str: str | None) -> str:
    if not image_str:
        return ""

    try:
        if image_str.startswith("file://"):
            # convert relative path to absolute, if needed
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
        print(f"OCR error: {e}")
        return ""


@app.post("/api/")
async def answer_question(query: Query):
    image_text = extract_text_from_image(query.image)
    combined_input = query.question + "\n" + image_text if image_text else query.question

    top_chunks = get_top_chunks(combined_input)
    answer, links = generate_answer(query.question, top_chunks)

    return {"answer": answer, "links": links}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)