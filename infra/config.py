from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings.

    Reads from environment variables or .env file.
    Prefix: None (reads directly, e.g. OLLAMA_BASE_URL)
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    # Environment
    ENVIRONMENT: Literal["development", "production", "testing"] = "development"
    LOG_LEVEL: str = "INFO"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_TIMEOUT: float = 60.0

    # Database
    DATABASE_URL: str = "sqlite:///./data/guiollama.db"

    # Chainlit
    CHAINLIT_HOST: str = "0.0.0.0"
    CHAINLIT_PORT: int = 8000


@lru_cache
def get_settings() -> Settings:
    return Settings()
