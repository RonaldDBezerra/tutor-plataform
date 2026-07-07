"""Knowledge source application service."""

from __future__ import annotations

import uuid

from app.core.exceptions import KnowledgeSourceNotFoundError, TutorNotFoundError
from app.db.uow import UnitOfWork
from app.knowledge.factory import KnowledgeProviderFactory
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
            tutor = await self.uow.tutors.get_by_id(tutor_id)
            if tutor is None:
                raise TutorNotFoundError(tutor_id)

            provider = KnowledgeProviderFactory.create(provider_type)
            await provider.validate(source_url, configuration=configuration)

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
                raise KnowledgeSourceNotFoundError(knowledge_source_id)

            await self.uow.knowledge.delete(knowledge_source)
            await self.uow.commit()

    async def update(
        self,
        knowledge_source_id: uuid.UUID,
        *,
        provider_type: ProviderType | None = None,
        source_name: str | None = None,
        source_url: str | None = None,
        configuration: dict[str, object] | None = None,
        enabled: bool | None = None,
    ) -> KnowledgeSource:
        async with self.uow:
            knowledge_source = await self.uow.knowledge.get_by_id(knowledge_source_id)
            if knowledge_source is None:
                raise KnowledgeSourceNotFoundError(knowledge_source_id)

            effective_provider_type = provider_type or knowledge_source.provider_type
            effective_source_url = source_url or knowledge_source.source_url
            effective_configuration = (
                configuration if configuration is not None else knowledge_source.configuration
            )

            provider = KnowledgeProviderFactory.create(effective_provider_type)
            await provider.validate(effective_source_url, configuration=effective_configuration)

            if provider_type is not None:
                knowledge_source.provider_type = provider_type
            if source_name is not None:
                knowledge_source.source_name = source_name
            if source_url is not None:
                knowledge_source.source_url = source_url
            if configuration is not None:
                knowledge_source.configuration = configuration
            if enabled is not None:
                knowledge_source.enabled = enabled

            updated_knowledge_source = await self.uow.knowledge.update(knowledge_source)
            await self.uow.commit()
            return updated_knowledge_source
