"""Async SQLAlchemy unit of work."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.session import AsyncSessionLocal
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.knowledge_repository import KnowledgeRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.tutor_repository import TutorRepository


class UnitOfWork:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        self._session_factory = session_factory or AsyncSessionLocal
        self.session: AsyncSession | None = None
        self.tutors: TutorRepository | None = None
        self.knowledge: KnowledgeRepository | None = None
        self.conversations: ConversationRepository | None = None
        self.messages: MessageRepository | None = None

    async def __aenter__(self) -> UnitOfWork:
        self.session = self._session_factory()
        self.tutors = TutorRepository(self.session)
        self.knowledge = KnowledgeRepository(self.session)
        self.conversations = ConversationRepository(self.session)
        self.messages = MessageRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session is None:
            return

        try:
            if exc_type is not None:
                await self.rollback()
        finally:
            await self.close()

    async def commit(self) -> None:
        if self.session is None:
            return
        await self.session.commit()

    async def rollback(self) -> None:
        if self.session is None:
            return
        await self.session.rollback()

    async def close(self) -> None:
        if self.session is None:
            return
        await self.session.close()
        self.session = None
        self.tutors = None
        self.knowledge = None
        self.conversations = None
        self.messages = None
