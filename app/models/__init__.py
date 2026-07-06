"""SQLAlchemy ORM models for the Tutor Platform domain."""

from app.models.enums import ProviderType, TutorStatus
from app.models.knowledge_source import KnowledgeSource
from app.models.tutor import Tutor

__all__ = [
    "ProviderType",
    "TutorStatus",
    "KnowledgeSource",
    "Tutor",
]
"""ORM models package.

Intentionally empty for now — no entities have been implemented yet.

When models are added, import each of them here so that ``Base.metadata``
is fully populated when Alembic's ``env.py`` imports this package for
autogenerate support. Example (future):

    from app.models.user import User
    from app.models.course import Course

    __all__ = ["User", "Course"]
"""
