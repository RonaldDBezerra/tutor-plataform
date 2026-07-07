"""Conversation persistence operations."""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation


class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, conversation: Conversation) -> Conversation:
        self.session.add(conversation)
        await self.session.flush()
        return conversation

    async def get_by_id(self, conversation_id: uuid.UUID) -> Conversation | None:
        statement: Select[Conversation] = select(Conversation).where(
            Conversation.id == conversation_id
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_tutor_and_session(
        self,
        *,
        tutor_id: uuid.UUID,
        session_id: str,
    ) -> Conversation | None:
        statement: Select[Conversation] = select(Conversation).where(
            Conversation.tutor_id == tutor_id,
            Conversation.session_id == session_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_by_tutor(self, tutor_id: uuid.UUID) -> Sequence[Conversation]:
        statement: Select[Conversation] = (
            select(Conversation)
            .where(Conversation.tutor_id == tutor_id)
            .order_by(Conversation.created_at.desc())
        )
        result = await self.session.execute(statement)
        return result.scalars().all()
