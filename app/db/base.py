"""Declarative base for all ORM models.

Every future SQLAlchemy model in ``app/models`` must inherit from ``Base``
defined here. Keeping the base in its own module (separate from the engine
and from the models themselves) avoids circular imports:

    models -> import Base from app.db.base
    alembic/env.py -> import Base from app.db.base (to read metadata)

No engine, session, or model definitions belong in this file.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all declarative ORM models in the application."""

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
