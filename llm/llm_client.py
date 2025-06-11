# llm_client.py

import httpx
import tiktoken

class LLMClient:
    def __init__(self, base_url: str, api_key: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat(self, messages):
        url = f"{self.base_url}/chat/completions"
        data = {
            "model": self.model,
            "messages": messages
        }

        try:
            response = httpx.post(url, headers=self.headers, json=data, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.ReadTimeout:
            raise Exception("API request timed out. Try increasing the timeout or check your network/API status.")
        except httpx.HTTPStatusError as err:
            raise Exception(f"HTTP error: {err.response.status_code} - {err.response.text}")

    def count_tokens(self, messages):
        """Estimate token count locally using tiktoken."""
        try:
            enc = tiktoken.encoding_for_model("gpt-4")  # Closest approx for gpt-4o-mini
        except Exception:
            enc = tiktoken.get_encoding("cl100k_base")

        num_tokens = 0
        for message in messages:
            num_tokens += 4  # Base tokens per message (OpenAI format)
            for key, value in message.items():
                num_tokens += len(enc.encode(value))
        num_tokens += 2  # For assistant priming
        return num_tokens
    
    def get_embedding(self, inputs: list):
        """
        Call the /embeddings endpoint with a list of input strings (e.g., queries or docs).
        Returns: list of embeddings (list of floats per input).
        """
        url = f"{self.base_url}/embeddings"
        data = {
            "model": self.model,
            "input": inputs
        }

        try:
            response = httpx.post(url, headers=self.headers, json=data, timeout=30.0)
            response.raise_for_status()
            return [item["embedding"] for item in response.json().get("data", [])]
        except httpx.HTTPStatusError as err:
            raise Exception(f"HTTP error: {err.response.status_code} - {err.response.text}")
        except KeyError:
            raise Exception(f"Invalid response structure: {response.json()}")