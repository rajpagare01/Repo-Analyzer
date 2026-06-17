import os
import requests
from .base_provider import BaseProvider

class GeminiProvider(BaseProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = "gemini-1.5-flash"
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def generate_review(self, prompt: str) -> str:
        if not self.api_key:
            print("[Gemini Error] GEMINI_API_KEY not set")
            return "{}"

        url = f"{self.base_url}?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"[Gemini Error] {str(e)}")
            return "{}"
