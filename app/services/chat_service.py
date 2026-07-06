"""Chat domain service for conversation persistence."""

from __future__ import annotations

import uuid

from app.db.uow import UnitOfWork
from app.models.conversation import Conversation
from app.models.enums import MessageRole
from app.models.message import Message


class ChatService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def get_or_create_conversation(
        self,
        *,
        tutor_id: uuid.UUID,
        session_id: str,
    ) -> Conversation:
        async with self.uow:
            tutor = await self.uow.tutors.get_by_id(tutor_id)
            if tutor is None:
                raise ValueError(f"Tutor not found: {tutor_id}")

            conversation = await self.uow.conversations.get_by_tutor_and_session(
                tutor_id=tutor_id,
                session_id=session_id,
            )
            if conversation is not None:
                return conversation

            conversation = Conversation(tutor_id=tutor_id, session_id=session_id)
            created_conversation = await self.uow.conversations.create(conversation)
            await self.uow.commit()
            return created_conversation

    async def save_user_message(
        self,
        *,
        conversation_id: uuid.UUID,
        content: str,
    ) -> Message:
        return await self._save_message(
            conversation_id=conversation_id,
            content=content,
            role=MessageRole.USER,
        )

    async def save_assistant_message(
        self,
        *,
        conversation_id: uuid.UUID,
        content: str,
    ) -> Message:
        return await self._save_message(
            conversation_id=conversation_id,
            content=content,
            role=MessageRole.ASSISTANT,
        )

    async def get_conversation_history(self, conversation_id: uuid.UUID) -> list[Message]:
        async with self.uow:
            messages = await self.uow.messages.list_by_conversation(conversation_id)
            return list(messages)

    async def _save_message(
        self,
        *,
        conversation_id: uuid.UUID,
        content: str,
        role: MessageRole,
    ) -> Message:
        async with self.uow:
            conversation = await self.uow.conversations.get_by_id(conversation_id)
            if conversation is None:
                raise ValueError(f"Conversation not found: {conversation_id}")

            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
            )
            created_message = await self.uow.messages.create(message)
            await self.uow.commit()
            return created_message
