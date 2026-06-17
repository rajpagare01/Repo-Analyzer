import os
import requests
from .base_provider import BaseProvider

class OpenAIProvider(BaseProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4-turbo"
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def generate_review(self, prompt: str) -> str:
        if not self.api_key:
            print("[OpenAI Error] OPENAI_API_KEY not set")
            return "{}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[OpenAI Error] {str(e)}")
            return "{}"
