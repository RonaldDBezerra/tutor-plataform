"""Tutor persistence operations."""

from __future__ import annotations

from typing import Sequence
import uuid

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enums import TutorStatus
from app.models.tutor import Tutor


class TutorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, tutor: Tutor) -> Tutor:
        self.session.add(tutor)
        await self.session.flush()
        return tutor

    async def get_by_id(self, tutor_id: uuid.UUID) -> Tutor | None:
        statement: Select[Tutor] = select(Tutor).options(selectinload(Tutor.knowledge_sources)).where(Tutor.id == tutor_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list(self, *, status: TutorStatus | None = None) -> Sequence[Tutor]:
        statement: Select[Tutor] = select(Tutor).options(selectinload(Tutor.knowledge_sources))
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
