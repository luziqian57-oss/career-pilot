from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Provider-neutral interface used by agents and services."""

    @abstractmethod
    async def generate_text(self, *, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def generate_structured(
        self, *, system_prompt: str, user_prompt: str, response_model: type[T]
    ) -> T:
        raise NotImplementedError

    async def close(self) -> None:
        """Release provider resources when needed."""
        return None

    @property
    def metadata(self) -> dict[str, Any]:
        return {"provider": self.__class__.__name__}
