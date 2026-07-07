"""Orchestration tool that resolves knowledge sources through providers."""

from __future__ import annotations

import logging

from app.knowledge.exceptions import KnowledgeLayerException
from app.knowledge.factory import KnowledgeProviderFactory
from app.knowledge.models import KnowledgeResult
from app.models.knowledge_source import KnowledgeSource

logger = logging.getLogger(__name__)


class KnowledgeTool:
    """Resolve a knowledge source through the correct provider."""

    async def get_context(
        self,
        knowledge_source: KnowledgeSource,
        question: str | None = None,
    ) -> KnowledgeResult:
        try:
            provider = KnowledgeProviderFactory.create(knowledge_source.provider_type)
            return await provider.get_context(
                source=knowledge_source.source_url,
                question=question,
                configuration=knowledge_source.configuration,
            )
        except KnowledgeLayerException:
            logger.exception(
                "Knowledge provider failed for source_id=%s source_name=%s provider_type=%s",
                knowledge_source.id,
                knowledge_source.source_name,
                knowledge_source.provider_type,
            )
            raise
        except Exception:
            error_message = (
                "Unexpected error while resolving knowledge "
                f"source_id={knowledge_source.id} "
                f"source_name={knowledge_source.source_name} "
                f"provider_type={knowledge_source.provider_type}"
            )
            logger.exception(
                error_message,
            )
            raise

    async def get_contexts(
        self,
        knowledge_sources: list[KnowledgeSource],
        question: str | None = None,
    ) -> list[KnowledgeResult]:
        results: list[KnowledgeResult] = []

        for knowledge_source in knowledge_sources:
            try:
                result = await self.get_context(knowledge_source, question=question)
            except Exception:
                continue

            results.append(result)

        return results
