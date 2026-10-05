from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Task-manager app"
    ENVIRONMENT: Literal["development", "production"] = "development"
    API_PREFIX: str = "/api/v1"

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:123456@localhost:15432/task-manager-db"
    )

    SECRET_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
