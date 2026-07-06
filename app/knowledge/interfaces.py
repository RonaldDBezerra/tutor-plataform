"""Provider contract for the knowledge layer."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.knowledge.models import KnowledgeResult


class KnowledgeProvider(ABC):
    """Common async contract implemented by all knowledge providers."""

    @abstractmethod
    async def validate(
        self,
        source: str,
        configuration: dict | None = None,
    ) -> None:
        """Validate that the source can be processed by the provider."""

    @abstractmethod
    async def get_context(
        self,
        source: str,
        question: str | None = None,
        configuration: dict | None = None,
    ) -> KnowledgeResult:
        """Return a normalized knowledge result for the requested source."""
