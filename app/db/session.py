"""Persistence-layer session access point.

This module re-exports the engine, session factory and FastAPI dependency
defined in ``app.core.database``. The reasoning for this indirection:

- ``app/core`` owns *configuration and bootstrapping* (how the engine is
  built from Settings).
- ``app/db`` owns the *persistence layer contract* consumed by the rest of
  the application (models, repositories, Alembic).

Future application code (services, repositories, tests, Alembic's
``env.py``) should depend on ``app.db.session`` rather than reaching into
``app.core.database`` directly. This keeps a clean boundary: if the engine
bootstrap changes internally, only this module's imports need review.
"""

from app.core.database import AsyncSessionLocal, engine, get_db

__all__ = ["engine", "AsyncSessionLocal", "get_db"]
