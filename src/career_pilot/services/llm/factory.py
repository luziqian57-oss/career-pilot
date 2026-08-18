from career_pilot.config import Settings
from career_pilot.services.llm.base import LLMProvider
from career_pilot.services.llm.mock import MockLLMProvider
from career_pilot.services.llm.openai import OpenAIProvider


def create_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        return OpenAIProvider(
            api_key=settings.openai_api_key,
            model=settings.llm_model,
            timeout=settings.llm_timeout_seconds,
        )
    return MockLLMProvider()
