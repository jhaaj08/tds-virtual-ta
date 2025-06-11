import os
from dotenv import load_dotenv
from openai import OpenAI
from openai.types import Model

load_dotenv()

client = OpenAI(
    api_key=os.getenv("AIPIPE_TOKEN"),
    base_url="https://aiproxy.sanand.workers.dev/openai/v1"
)

try:
    models = client.models.list()
    print("✅ Token is valid. Available models:")
    for model in models.data:
        print("-", model.id)
except Exception as e:
    print("❌ Error:", e)