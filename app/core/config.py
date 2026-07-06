"""Application configuration.

Centralizes all environment-driven configuration using Pydantic Settings.
This is the single source of truth for runtime configuration values.
No business logic should live here — only settings declaration and loading.
"""

from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings(BaseSettings):
    """Runtime application settings, loaded from environment variables or .env file.

    Attributes:
        DATABASE_URL: Async SQLAlchemy connection string
            (must use the ``postgresql+asyncpg://`` driver prefix).
        DB_ECHO: Whether SQLAlchemy should log emitted SQL statements.
            Useful for local debugging, should be False in production.
        DB_POOL_SIZE: Number of persistent connections kept in the pool.
        DB_MAX_OVERFLOW: Number of extra connections allowed beyond DB_POOL_SIZE
            during load spikes.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Database ---
    DATABASE_URL: str = Field(
        ...,
        description="Async PostgreSQL connection string (postgresql+asyncpg://...)",
    )

    # --- AI / LangChain ---
    OPENAI_API_KEY: str | None = Field(default=None, description="OpenAI API key used by LangChain")
    LLM_MODEL: str = Field(default="gpt-5.4-mini", description="Default LLM model name")
    LLM_TEMPERATURE: float = Field(default=0.0, description="Default model temperature")
    TAVILY_API_KEY: str | None = Field(default=None, description="Tavily API key used by the Extract provider")
    TAVILY_API_BASE_URL: str | None = Field(default=None, description="Optional Tavily API base URL override")
    TAVILY_TIMEOUT_SECONDS: float = Field(default=30.0, description="Timeout for Tavily provider operations")
    LANGSMITH_TRACING: bool = Field(default=False, description="Enable LangSmith tracing")
    LANGSMITH_ENDPOINT: str = Field(
        default="https://api.smith.langchain.com",
        description="LangSmith API endpoint",
    )
    LANGSMITH_API_KEY: str | None = Field(default=None, description="LangSmith API key")
    LANGSMITH_PROJECT: str | None = Field(default=None, description="LangSmith project name")

    DB_ECHO: bool = Field(default=False, description="Log all SQL statements emitted by SQLAlchemy")
    DB_POOL_SIZE: int = Field(default=5, description="Base size of the async connection pool")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Extra connections allowed beyond DB_POOL_SIZE")


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of :class:`Settings`.

    Using ``lru_cache`` ensures the environment is parsed only once per process,
    and allows Settings to be injected as a FastAPI dependency later if needed.
    """

    return Settings()


settings: Settings = get_settings()
