"""Knowledge source application service."""

from __future__ import annotations

import uuid

from app.db.uow import UnitOfWork
from app.models.enums import ProviderType
from app.models.knowledge_source import KnowledgeSource


class KnowledgeService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def create(
        self,
        *,
        tutor_id: uuid.UUID,
        provider_type: ProviderType,
        source_name: str,
        source_url: str,
        configuration: dict[str, object],
        enabled: bool,
    ) -> KnowledgeSource:
        async with self.uow:
            knowledge_source = KnowledgeSource(
                tutor_id=tutor_id,
                provider_type=provider_type,
                source_name=source_name,
                source_url=source_url,
                configuration=configuration,
                enabled=enabled,
            )
            created_knowledge_source = await self.uow.knowledge.create(knowledge_source)
            await self.uow.commit()
            return created_knowledge_source

    async def list_by_tutor(self, tutor_id: uuid.UUID) -> list[KnowledgeSource]:
        async with self.uow:
            knowledge_sources = await self.uow.knowledge.list_by_tutor(tutor_id)
            return list(knowledge_sources)

    async def delete(self, knowledge_source_id: uuid.UUID) -> None:
        async with self.uow:
            knowledge_source = await self.uow.knowledge.get_by_id(knowledge_source_id)
            if knowledge_source is None:
                return

            await self.uow.knowledge.delete(knowledge_source)
            await self.uow.commit()
