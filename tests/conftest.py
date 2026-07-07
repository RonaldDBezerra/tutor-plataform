from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import (
    get_chat_service,
    get_knowledge_service,
    get_tutor_agent,
    get_tutor_service,
)
from app.core import config as app_config
from app.main import app
from app.models.enums import MessageRole, ProviderType, TutorStatus

TEST_ADMIN_API_KEY = "test-admin-key"


def make_timestamp() -> datetime:
    return datetime.now(timezone.utc)


def make_tutor(
    tutor_id: UUID | None = None,
    *,
    embed_token: str | None = None,
    name: str = "Tutor Alpha",
    description: str | None = "Description",
    system_prompt: str = "System prompt",
    status: TutorStatus = TutorStatus.ACTIVE,
    knowledge_sources: list[object] | None = None,
):
    return SimpleNamespace(
        id=tutor_id or uuid4(),
        embed_token=embed_token or uuid4().hex,
        name=name,
        description=description,
        system_prompt=system_prompt,
        status=status,
        created_at=make_timestamp(),
        updated_at=make_timestamp(),
        knowledge_sources=knowledge_sources or [],
        instructions=system_prompt,
    )


def make_knowledge_source(
    knowledge_source_id: UUID | None = None,
    *,
    tutor_id: UUID,
    provider_type: ProviderType = ProviderType.HTTP_TEXT,
    source_name: str = "Source",
    source_url: str = "https://example.com",
    configuration: dict[str, object] | None = None,
    enabled: bool = True,
):
    return SimpleNamespace(
        id=knowledge_source_id or uuid4(),
        tutor_id=tutor_id,
        provider_type=provider_type,
        source_name=source_name,
        source_url=source_url,
        configuration=configuration or {},
        enabled=enabled,
        created_at=make_timestamp(),
        updated_at=make_timestamp(),
    )


def make_conversation(conversation_id: UUID | None = None, *, tutor_id: UUID, session_id: str):
    return SimpleNamespace(
        id=conversation_id or uuid4(),
        tutor_id=tutor_id,
        session_id=session_id,
        created_at=make_timestamp(),
        updated_at=make_timestamp(),
    )


def make_message(*, conversation_id: UUID, role: MessageRole, content: str):
    return SimpleNamespace(
        id=uuid4(),
        conversation_id=conversation_id,
        role=role,
        content=content,
        created_at=make_timestamp(),
    )


class FakeTutorService:
    def __init__(self) -> None:
        self.tutors: dict[UUID, SimpleNamespace] = {}

    async def create(
        self, *, name: str, description: str | None, system_prompt: str, status: TutorStatus
    ):
        tutor = make_tutor(
            name=name, description=description, system_prompt=system_prompt, status=status
        )
        self.tutors[tutor.id] = tutor
        return tutor

    async def list(self, *, status: TutorStatus | None = None):
        tutors = list(self.tutors.values())
        if status is not None:
            tutors = [tutor for tutor in tutors if tutor.status == status]
        return tutors

    async def get_by_id(self, tutor_id: UUID):
        return self.tutors.get(tutor_id)

    async def get_by_embed_token(self, embed_token: str):
        return next(
            (tutor for tutor in self.tutors.values() if tutor.embed_token == embed_token), None
        )

    async def update(
        self,
        tutor_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        system_prompt: str | None = None,
        status: TutorStatus | None = None,
    ):
        tutor = self.tutors[tutor_id]
        if name is not None:
            tutor.name = name
        if description is not None:
            tutor.description = description
        if system_prompt is not None:
            tutor.system_prompt = system_prompt
            tutor.instructions = system_prompt
        if status is not None:
            tutor.status = status
        tutor.updated_at = make_timestamp()
        return tutor

    async def delete(self, tutor_id: UUID):
        tutor = self.tutors[tutor_id]
        tutor.status = TutorStatus.INACTIVE
        tutor.updated_at = make_timestamp()
        return tutor


class FakeKnowledgeService:
    def __init__(self, tutor_service: FakeTutorService) -> None:
        self.tutor_service = tutor_service
        self.sources: dict[UUID, SimpleNamespace] = {}

    async def create(
        self,
        *,
        tutor_id: UUID,
        provider_type: ProviderType,
        source_name: str,
        source_url: str,
        configuration: dict[str, object],
        enabled: bool,
    ):
        source = make_knowledge_source(
            tutor_id=tutor_id,
            provider_type=provider_type,
            source_name=source_name,
            source_url=source_url,
            configuration=configuration,
            enabled=enabled,
        )
        self.sources[source.id] = source
        self.tutor_service.tutors[tutor_id].knowledge_sources.append(source)
        return source

    async def list_by_tutor(self, tutor_id: UUID):
        return [source for source in self.sources.values() if source.tutor_id == tutor_id]

    async def update(
        self,
        knowledge_source_id: UUID,
        *,
        provider_type: ProviderType | None = None,
        source_name: str | None = None,
        source_url: str | None = None,
        configuration: dict[str, object] | None = None,
        enabled: bool | None = None,
    ):
        source = self.sources[knowledge_source_id]
        if provider_type is not None:
            source.provider_type = provider_type
        if source_name is not None:
            source.source_name = source_name
        if source_url is not None:
            source.source_url = source_url
        if configuration is not None:
            source.configuration = configuration
        if enabled is not None:
            source.enabled = enabled
        source.updated_at = make_timestamp()
        return source

    async def delete(self, knowledge_source_id: UUID):
        self.sources.pop(knowledge_source_id)


class FakeChatService:
    def __init__(self, tutor_service: FakeTutorService) -> None:
        self.tutor_service = tutor_service
        self.conversations: dict[str, SimpleNamespace] = {}
        self.messages: list[SimpleNamespace] = []
        self.messages_by_conversation: dict[UUID, list[SimpleNamespace]] = {}

    async def get_tutor(self, tutor_id: UUID):
        return self.tutor_service.tutors.get(tutor_id)

    async def get_or_create_conversation(self, *, tutor_id: UUID, session_id: str):
        conversation = self.conversations.get(session_id)
        if conversation is None:
            conversation = make_conversation(tutor_id=tutor_id, session_id=session_id)
            self.conversations[session_id] = conversation
            self.messages_by_conversation[conversation.id] = []
        return conversation

    async def get_conversation_history(self, conversation_id: UUID):
        return list(self.messages_by_conversation.get(conversation_id, []))

    async def save_user_message(self, *, conversation_id: UUID, content: str):
        message = make_message(
            conversation_id=conversation_id, role=MessageRole.USER, content=content
        )
        self.messages.append(message)
        self.messages_by_conversation.setdefault(conversation_id, []).append(message)
        return message

    async def save_assistant_message(self, *, conversation_id: UUID, content: str):
        message = make_message(
            conversation_id=conversation_id, role=MessageRole.ASSISTANT, content=content
        )
        self.messages.append(message)
        self.messages_by_conversation.setdefault(conversation_id, []).append(message)
        return message


class FakeTutorAgent:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def run(self, tutor, question: str, history=None) -> str:
        self.calls.append(
            {"tutor_id": tutor.id, "question": question, "history": list(history or [])}
        )
        return f"Answer for {tutor.name}: {question}"


@pytest.fixture()
def fake_services() -> dict[str, object]:
    tutor_service = FakeTutorService()
    knowledge_service = FakeKnowledgeService(tutor_service)
    chat_service = FakeChatService(tutor_service)
    tutor_agent = FakeTutorAgent()
    return {
        "tutor_service": tutor_service,
        "knowledge_service": knowledge_service,
        "chat_service": chat_service,
        "tutor_agent": tutor_agent,
    }


@pytest.fixture()
def client(fake_services: dict[str, object]) -> Iterator[TestClient]:
    previous_admin_api_key = app_config.settings.ADMIN_API_KEY
    app_config.settings.ADMIN_API_KEY = TEST_ADMIN_API_KEY

    app.dependency_overrides[get_tutor_service] = lambda: fake_services["tutor_service"]
    app.dependency_overrides[get_knowledge_service] = lambda: fake_services["knowledge_service"]
    app.dependency_overrides[get_chat_service] = lambda: fake_services["chat_service"]
    app.dependency_overrides[get_tutor_agent] = lambda: fake_services["tutor_agent"]

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    app_config.settings.ADMIN_API_KEY = previous_admin_api_key


@pytest.fixture()
def admin_headers() -> dict[str, str]:
    return {"X-ADMIN-KEY": TEST_ADMIN_API_KEY}
