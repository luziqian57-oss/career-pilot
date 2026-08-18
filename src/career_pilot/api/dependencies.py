from fastapi import Request

from career_pilot.services.llm.base import LLMProvider


def get_llm(request: Request) -> LLMProvider:
    return request.app.state.llm
