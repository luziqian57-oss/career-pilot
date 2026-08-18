from typing import TypeVar

from pydantic import BaseModel

from career_pilot.services.llm.base import LLMProvider

T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(LLMProvider):
    """Offline provider for development and tests."""

    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        return "Mock response: configure LLM_PROVIDER=openai for model-generated content."

    async def generate_structured(
        self, *, system_prompt: str, user_prompt: str, response_model: type[T]
    ) -> T:
        raise NotImplementedError(
            "Mock structured responses are supplied by deterministic services."
        )
