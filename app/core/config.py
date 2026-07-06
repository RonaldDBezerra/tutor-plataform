"""Application configuration.

Centralizes all environment-driven configuration using Pydantic Settings.
This is the single source of truth for runtime configuration values.
No business logic should live here — only settings declaration and loading.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
