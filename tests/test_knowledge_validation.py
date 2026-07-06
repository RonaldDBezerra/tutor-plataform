from __future__ import annotations

import asyncio
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.exceptions import TutorNotFoundError
from app.knowledge.exceptions import InvalidKnowledgeSourceException
from app.knowledge.models import KnowledgeResult
from app.models.enums import ProviderType, TutorStatus
from app.models.knowledge_source import KnowledgeSource
from app.models.tutor import Tutor
from app.services.knowledge_service import KnowledgeService
from app.knowledge.providers.tavily_provider import TavilyProvider


class FakeTutorRepository:
    def __init__(self, tutor: Tutor | None) -> None:
        self.tutor = tutor

    async def get_by_id(self, tutor_id):
        return self.tutor


class FakeKnowledgeRepository:
    def __init__(self) -> None:
        self.created: list[KnowledgeSource] = []
        self.updated: list[KnowledgeSource] = []

    async def create(self, knowledge_source: KnowledgeSource) -> KnowledgeSource:
        self.created.append(knowledge_source)
        return knowledge_source

    async def get_by_id(self, knowledge_source_id):
        return self.created[0] if self.created else None

    async def update(self, knowledge_source: KnowledgeSource) -> KnowledgeSource:
        self.updated.append(knowledge_source)
        return knowledge_source

    async def list_by_tutor(self, tutor_id):
        return []

    async def delete(self, knowledge_source):
        return None


class FakeUow:
    def __init__(self, tutor: Tutor | None) -> None:
        self.tutors = FakeTutorRepository(tutor)
        self.knowledge = FakeKnowledgeRepository()
        self.commits = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return None

    async def commit(self):
        self.commits += 1


class SuccessfulProvider:
    def __init__(self) -> None:
        self.validations: list[tuple[str, dict | None]] = []

    async def validate(self, source: str, configuration: dict | None = None) -> None:
        self.validations.append((source, configuration))


class InvalidProvider:
    async def validate(self, source: str, configuration: dict | None = None) -> None:
        raise InvalidKnowledgeSourceException("invalid source")


class FakeTavilyExtract:
    instances: list["FakeTavilyExtract"] = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.calls: list[dict[str, object]] = []
        FakeTavilyExtract.instances.append(self)

    async def ainvoke(self, payload):
        self.calls.append(payload)
        return {
            "results": [
                {"url": payload["urls"][0], "raw_content": "Extracted Tavily content"},
            ],
            "failed_results": [],
            "response_time": 0.12,
        }


class SlowTavilyExtract:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    async def ainvoke(self, payload):
        await asyncio.sleep(0.05)
        return {
            "results": [{"url": payload["urls"][0], "raw_content": "Too late"}],
            "failed_results": [],
            "response_time": 0.05,
        }


@pytest.mark.asyncio
async def test_knowledge_source_create_validates_before_persisting(monkeypatch):
    tutor = Tutor(name="Tutor", description=None, system_prompt="Prompt", status=TutorStatus.ACTIVE)
    service = KnowledgeService(FakeUow(tutor))
    provider = SuccessfulProvider()

    monkeypatch.setattr("app.services.knowledge_service.KnowledgeProviderFactory.create", lambda provider_type: provider)

    result = await service.create(
        tutor_id=uuid4(),
        provider_type=ProviderType.HTTP_TEXT,
        source_name="Docs",
        source_url="https://example.com/docs",
        configuration={"timeout": 2},
        enabled=True,
    )

    assert result.source_url == "https://example.com/docs"
    assert provider.validations == [("https://example.com/docs", {"timeout": 2})]
    assert service.uow.knowledge.created
    assert service.uow.commits == 1


@pytest.mark.asyncio
async def test_knowledge_source_create_rejects_invalid_source(monkeypatch):
    tutor = Tutor(name="Tutor", description=None, system_prompt="Prompt", status=TutorStatus.ACTIVE)
    service = KnowledgeService(FakeUow(tutor))

    monkeypatch.setattr("app.services.knowledge_service.KnowledgeProviderFactory.create", lambda provider_type: InvalidProvider())

    with pytest.raises(InvalidKnowledgeSourceException):
        await service.create(
            tutor_id=uuid4(),
            provider_type=ProviderType.JSON,
            source_name="Broken",
            source_url="https://example.com/broken",
            configuration={},
            enabled=True,
        )

    assert not service.uow.knowledge.created
    assert service.uow.commits == 0


@pytest.mark.asyncio
async def test_tavily_provider_extracts_content(monkeypatch):
    FakeTavilyExtract.instances.clear()
    monkeypatch.setattr("app.knowledge.providers.tavily_provider.TavilyExtract", FakeTavilyExtract)

    provider = TavilyProvider(api_key="test-key", timeout_seconds=1)
    result = await provider.get_context(
        "https://example.com/article",
        configuration={"extract_depth": "advanced", "include_images": True},
    )

    assert result.provider == "TavilyProvider"
    assert result.source == "https://example.com/article"
    assert "Extracted Tavily content" in result.content
    assert FakeTavilyExtract.instances[0].kwargs["tavily_api_key"] == "test-key"
    assert FakeTavilyExtract.instances[0].calls[0]["urls"] == ["https://example.com/article"]


@pytest.mark.asyncio
async def test_tavily_provider_respects_timeout(monkeypatch):
    monkeypatch.setattr("app.knowledge.providers.tavily_provider.TavilyExtract", SlowTavilyExtract)

    provider = TavilyProvider(api_key="test-key", timeout_seconds=0.01)

    with pytest.raises(InvalidKnowledgeSourceException):
        await provider.validate("https://example.com/slow")
