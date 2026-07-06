"""Repository layer for persistence access."""

from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.tutor_repository import TutorRepository

__all__ = ["KnowledgeRepository", "TutorRepository"]
