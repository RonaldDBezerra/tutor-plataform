"""Knowledge source persistence operations."""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge_source import KnowledgeSource


class KnowledgeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, knowledge_source: KnowledgeSource) -> KnowledgeSource:
        self.session.add(knowledge_source)
        await self.session.flush()
        return knowledge_source

    async def list_by_tutor(self, tutor_id: uuid.UUID) -> Sequence[KnowledgeSource]:
        statement: Select[KnowledgeSource] = (
            select(KnowledgeSource)
            .where(KnowledgeSource.tutor_id == tutor_id)
            .order_by(KnowledgeSource.created_at.desc())
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_id(self, knowledge_source_id: uuid.UUID) -> KnowledgeSource | None:
        statement: Select[KnowledgeSource] = select(KnowledgeSource).where(
            KnowledgeSource.id == knowledge_source_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update(self, knowledge_source: KnowledgeSource) -> KnowledgeSource:
        merged_knowledge_source = await self.session.merge(knowledge_source)
        await self.session.flush()
        await self.session.refresh(merged_knowledge_source)
        return merged_knowledge_source

    async def delete(self, knowledge_source: KnowledgeSource) -> None:
        await self.session.delete(knowledge_source)
        await self.session.flush()
