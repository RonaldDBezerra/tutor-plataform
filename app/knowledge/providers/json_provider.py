"""JSON endpoint knowledge provider."""

from __future__ import annotations

import json

import httpx

from app.knowledge.exceptions import InvalidKnowledgeSourceException
from app.knowledge.interfaces import KnowledgeProvider
from app.knowledge.models import KnowledgeResult


class JsonProvider(KnowledgeProvider):
    """Fetch JSON content and normalize it into plain text."""

    async def validate(self, source: str, configuration: dict | None = None) -> None:
        await self.get_context(source=source, configuration=configuration)

    async def get_context(
        self,
        source: str,
        question: str | None = None,
        configuration: dict | None = None,
    ) -> KnowledgeResult:
        if not source.strip():
            raise InvalidKnowledgeSourceException("JSON provider requires a non-empty source URL")

        timeout = self._get_timeout(configuration)

        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.get(source)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            raise InvalidKnowledgeSourceException(
                f"JSON provider failed for source {source!r}: {exc.response.status_code}"
            ) from exc
        except (httpx.RequestError, ValueError) as exc:
            raise InvalidKnowledgeSourceException(
                f"JSON provider could not decode source {source!r}: {exc}"
            ) from exc

        content = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
        metadata = {
            "status_code": response.status_code,
            "content_type": response.headers.get("content-type"),
            "question": question,
        }
        return KnowledgeResult(
            content=content,
            metadata=metadata,
            provider=self.__class__.__name__,
            source=source,
        )

    def _get_timeout(self, configuration: dict | None) -> float:
        if not configuration:
            return 10.0

        timeout = configuration.get("timeout")
        if timeout is None:
            return 10.0

        try:
            return float(timeout)
        except (TypeError, ValueError) as exc:
            raise InvalidKnowledgeSourceException("Invalid timeout configuration for JSON provider") from exc