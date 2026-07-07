from __future__ import annotations

from uuid import uuid4

import pytest

from app.models.enums import TutorStatus
from app.models.tutor import Tutor
from app.repositories.tutor_repository import TutorRepository


class _FakeResult:
    def __init__(self, tutor: Tutor | None) -> None:
        self._tutor = tutor

    def scalar_one_or_none(self) -> Tutor | None:
        return self._tutor


class _FakeSession:
    def __init__(self, tutor: Tutor | None) -> None:
        self.tutor = tutor
        self.statements: list[object] = []

    async def execute(self, statement):
        self.statements.append(statement)
        return _FakeResult(self.tutor)


@pytest.mark.asyncio
async def test_get_by_embed_token_builds_lookup_query():
    tutor = Tutor(
        id=uuid4(),
        embed_token="token-123",
        name="Tutor",
        description=None,
        system_prompt="Prompt",
        status=TutorStatus.ACTIVE,
    )
    session = _FakeSession(tutor)
    repository = TutorRepository(session)

    found_tutor = await repository.get_by_embed_token("token-123")

    assert found_tutor is tutor
    assert "embed_token" in str(session.statements[0])