from typing import TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from career_pilot.services.llm.base import LLMProvider

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(LLMProvider):
    def __init__(self, *, api_key: str, model: str, timeout: float) -> None:
        self._client = AsyncOpenAI(api_key=api_key, timeout=timeout)
        self._model = model

    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""

    async def generate_structured(
        self, *, system_prompt: str, user_prompt: str, response_model: type[T]
    ) -> T:
        response = await self._client.beta.chat.completions.parse(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=response_model,
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise RuntimeError("The model did not return a valid structured response.")
        return parsed

    async def close(self) -> None:
        await self._client.close()
