import os
from .providers import BaseProvider, OllamaProvider, GeminiProvider, OpenAIProvider

class LLMFactory:
    @staticmethod
    def get_provider() -> BaseProvider:
        # Default to Ollama as requested by user for local execution
        provider_name = os.getenv("LLM_PROVIDER", "ollama").lower()
        
        if provider_name == "openai":
            return OpenAIProvider()
        elif provider_name == "gemini":
            return GeminiProvider()
        else:
            return OllamaProvider(model_name="llama3")
