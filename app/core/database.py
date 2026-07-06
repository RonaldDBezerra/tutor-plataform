"""Database engine and session bootstrap.

This module is responsible for creating the SQLAlchemy async engine and the
session factory used across the application. It contains no business logic
and no models — only infrastructure wiring.

The FastAPI dependency ``get_db`` is defined here because it depends directly
on the engine/session factory created in this module.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# --- Engine -----------------------------------------------------------------
# A single engine instance is shared by the whole application. It manages the
# underlying connection pool to PostgreSQL via the asyncpg driver.
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    future=True,
)

# --- Session factory ----------------------------------------------------------
# `expire_on_commit=False` keeps ORM instances usable after commit, which is
# the expected behavior in typical FastAPI request/response cycles.
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a scoped :class:`AsyncSession`.

    Usage::

        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)) -> ...:
            ...

    The session is always closed at the end of the request, even if an
    exception is raised. Commit/rollback of business transactions is the
    responsibility of the calling code (service/repository layer), not of
    this dependency.
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
