"""Tutor persistence operations."""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import TutorStatus
from app.models.tutor import Tutor


class TutorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _base_statement(self) -> Select[Tutor]:
        return select(Tutor).options(selectinload(Tutor.knowledge_sources))

    async def create(self, tutor: Tutor) -> Tutor:
        self.session.add(tutor)
        await self.session.flush()
        return tutor

    async def get_by_id(self, tutor_id: uuid.UUID) -> Tutor | None:
        statement = self._base_statement().where(Tutor.id == tutor_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_embed_token(self, embed_token: str) -> Tutor | None:
        statement = self._base_statement().where(Tutor.embed_token == embed_token)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list(self, *, status: TutorStatus | None = None) -> Sequence[Tutor]:
        statement = self._base_statement()
        if status is not None:
            statement = statement.where(Tutor.status == status)
        statement = statement.order_by(Tutor.created_at.desc())
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def update(self, tutor: Tutor) -> Tutor:
        merged_tutor = await self.session.merge(tutor)
        await self.session.flush()
        await self.session.refresh(merged_tutor)
        return merged_tutor

    async def deactivate(self, tutor: Tutor) -> Tutor:
        tutor.status = TutorStatus.INACTIVE
        self.session.add(tutor)
        await self.session.flush()
        await self.session.refresh(tutor)
        return tutor
