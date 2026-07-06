"""Tavily knowledge provider placeholder."""

from __future__ import annotations

from app.knowledge.exceptions import InvalidKnowledgeSourceException, ProviderNotImplementedException
from app.knowledge.interfaces import KnowledgeProvider
from app.knowledge.models import KnowledgeResult


class TavilyProvider(KnowledgeProvider):
    """Placeholder for Tavily integration in a future sprint."""

    async def get_context(
        self,
        source: str,
        question: str | None = None,
        configuration: dict | None = None,
    ) -> KnowledgeResult:
        if not source.strip():
            raise InvalidKnowledgeSourceException("Tavily provider requires a non-empty source identifier")

        raise ProviderNotImplementedException("Tavily provider is not implemented yet")