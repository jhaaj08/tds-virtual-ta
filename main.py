from fastapi import FastAPI, Request
from pydantic import BaseModel
import base64
from PIL import Image
import io
import pytesseract
from dotenv import load_dotenv


from llm.response_generator import generate_answer
from retrieval.query_engine import get_top_chunks

load_dotenv()  # place this early in main.py
app = FastAPI()

class Query(BaseModel):
    question: str
    image: str | None = None  # Optional image

def extract_text_from_image(image_str: str) -> str:
    try:
        if image_str.startswith("file://"):
            # Read raw image bytes from file path
            filepath = image_str.replace("file://", "")
            with open(filepath, "rb") as f:
                image_data = f.read()
        else:
            # Decode base64 string
            image_data = base64.b64decode(image_str)

        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image)
        return text.strip()

    except Exception as e:
        print(f"OCR failed: {e}")
        return ""

@app.post("/api/")
async def answer_question(query: Query):
    # Step 1: Extract text from image if present
    image_text = extract_text_from_image(query.image) if query.image else ""
    
    # Step 2: Combine question + image text
    combined_input = query.question + "\n" + image_text if image_text else query.question

    # Step 3: Get relevant chunks and generate answer
    top_chunks = get_top_chunks(combined_input)
    answer, links = generate_answer(query.question, top_chunks)
    return {"answer": answer, "links": links}