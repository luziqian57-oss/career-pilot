from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False
    )

    app_name: str = "CareerPilot API"
    app_env: Literal["development", "test", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    llm_provider: Literal["mock", "openai"] = "mock"
    llm_model: str = "gpt-4o-mini"
    openai_api_key: str | None = Field(default=None, repr=False)
    llm_timeout_seconds: float = 30.0

    database_url: str = "postgresql+asyncpg://careerpilot:careerpilot@localhost:5432/careerpilot"
    redis_url: str = "redis://localhost:6379/0"
    max_upload_size_mb: int = Field(default=5, ge=1, le=25)
    max_extracted_text_characters: int = Field(default=50_000, ge=1_000, le=500_000)


@lru_cache
def get_settings() -> Settings:
    return Settings()
