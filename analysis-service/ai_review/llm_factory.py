import os
import logging
from .providers import BaseProvider, OllamaProvider, GeminiProvider, OpenAIProvider
from .providers.gemini_provider import ConfigurationError

logger = logging.getLogger('codepulse-analysis')


class LLMFactory:
    """
    Factory that resolves the active LLM provider and wraps calls
    with an optional Gemini → Ollama fallback at generation time.

    Environment Variables:
        LLM_PROVIDER        — "gemini" (default) | "openai" | "ollama"
        ENABLE_LLM_FALLBACK — "true" (default) to auto-fallback to Ollama
                               when Gemini fails at generation time.
        OLLAMA_MODEL        — Ollama model name, defaults to "llama3".
    """

    @staticmethod
    def _build_provider(name: str) -> BaseProvider:
        """Instantiate a provider by name. Raises on misconfiguration."""
        if name == "gemini":
            return GeminiProvider()
        elif name == "openai":
            return OpenAIProvider()
        else:
            model = os.getenv("OLLAMA_MODEL", "llama3")
            return OllamaProvider(model_name=model)

    @staticmethod
    def get_provider() -> BaseProvider:
        """
        Return the configured provider.

        If the requested provider is Gemini but it cannot be initialised
        (e.g. missing API key), fall back to Ollama immediately.
        """
        provider_name = os.getenv("LLM_PROVIDER", "gemini").lower()
        logger.info(f"LLM_PROVIDER requested: {provider_name}")

        try:
            provider = LLMFactory._build_provider(provider_name)
            logger.info(f"Using {provider.__class__.__name__}")
            return provider
        except ConfigurationError as e:
            logger.warning(f"Cannot initialise {provider_name}: {e}")
            if provider_name != "ollama":
                logger.warning("Falling back to OllamaProvider for this session")
                fallback = OllamaProvider(
                    model_name=os.getenv("OLLAMA_MODEL", "llama3")
                )
                return fallback
            raise

    @staticmethod
    def generate_with_fallback(prompt: str) -> tuple[str, str]:
        """
        Generate a review using the primary provider.

        If the primary provider is Gemini and generation fails at runtime
        (rate-limit, network error, timeout, outage), automatically retry
        with OllamaProvider — provided ENABLE_LLM_FALLBACK is enabled.

        Args:
            prompt: The full review prompt.

        Returns:
            A tuple of (Raw JSON string, Provider Name string).
        """
        provider = LLMFactory.get_provider()
        fallback_enabled = os.getenv("ENABLE_LLM_FALLBACK", "true").lower() == "true"
        
        # Determine the primary provider name as a simple string
        primary_name = "gemini" if "Gemini" in provider.__class__.__name__ else \
                       "openai" if "OpenAI" in provider.__class__.__name__ else "ollama"

        try:
            return provider.generate_review(prompt), primary_name
        except Exception as e:
            if fallback_enabled and primary_name != "ollama":
                logger.warning(
                    "Gemini generation failed. Falling back to Ollama."
                )
                try:
                    fallback = OllamaProvider(
                        model_name=os.getenv("OLLAMA_MODEL", "llama3")
                    )
                    return fallback.generate_review(prompt), "ollama_fallback"
                except Exception as fallback_err:
                    logger.error(f"Ollama fallback also failed: {fallback_err}")
                    return "{}", "failed"
            else:
                logger.error(
                    f"{primary_name} failed and fallback is disabled: {e}"
                )
                return "{}", "failed"
