"""Message persistence operations."""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, message: Message) -> Message:
        self.session.add(message)
        await self.session.flush()
        return message

    async def get_by_id(self, message_id: uuid.UUID) -> Message | None:
        statement: Select[Message] = select(Message).where(Message.id == message_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_by_conversation(self, conversation_id: uuid.UUID) -> Sequence[Message]:
        statement: Select[Message] = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        result = await self.session.execute(statement)
        return result.scalars().all()
