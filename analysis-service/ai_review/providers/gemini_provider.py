import os
import logging
from google import genai
from .base_provider import BaseProvider

logger = logging.getLogger('codepulse-analysis')


class ConfigurationError(Exception):
    """Raised when a required configuration value is missing."""
    pass


class GeminiProvider(BaseProvider):
    """
    AI review provider backed by Google Gemini (google-genai SDK).

    Requires:
        GEMINI_API_KEY environment variable.

    Model:
        gemini-2.5-flash (fast, JSON-capable)
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ConfigurationError(
                "GEMINI_API_KEY not found.\n"
                "Create a Gemini API key and add it to your .env file."
            )

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"

        logger.info("Using Gemini Provider")

    def generate_review(self, prompt: str) -> str:
        """
        Generate a review by calling the Gemini API.

        Args:
            prompt: The full review prompt including metrics.

        Returns:
            Raw JSON string from the model.

        Raises:
            Exception: Propagated to the caller (LLMFactory) so
                       fallback logic can catch it.
        """
        logger.info("Generating AI review via Gemini...")
        try:
            # We configure for JSON output using the new google-genai SDK syntax
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                )
            )
            result = response.text
            return result
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise  # Let the factory handle fallback
