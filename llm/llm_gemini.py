import google.generativeai as genai
import base64
import os 

api_key = os.getenv("GEMINI_API_KEY")
print(api_key)

# Set up Gemini
genai.configure(api_key=api_key)

def get_image_description(image_path: str) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")

    with open(image_path, "rb") as f:
        image_data = f.read()

    image_base64 = base64.b64encode(image_data).decode("utf-8")

    try:
        response = model.generate_content([
            {
                "mime_type": "image/png",  # or "image/jpeg" depending on your input
                "data": image_base64,
            },
            {
                "text": "A one-liner or short paragraph that captures just the semantic essence of the image for better relevance in RAG without bloating the embedding size."
            }
        ])
        return response.text
    except Exception as e:
        print(f"Error getting description: {e}")
        return "Image description unavailable."