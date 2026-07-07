"""HTTP-based knowledge provider."""

from __future__ import annotations

import json

import httpx

from app.knowledge.exceptions import InvalidKnowledgeSourceException
from app.knowledge.interfaces import KnowledgeProvider
from app.knowledge.models import KnowledgeResult


class HttpProvider(KnowledgeProvider):
    """Fetch plain text content from a public URL."""

    async def validate(self, source: str, configuration: dict | None = None) -> None:
        await self.get_context(source=source, configuration=configuration)

    async def get_context(
        self,
        source: str,
        question: str | None = None,
        configuration: dict | None = None,
    ) -> KnowledgeResult:
        if not source.strip():
            raise InvalidKnowledgeSourceException("HTTP provider requires a non-empty source URL")

        timeout = self._get_timeout(configuration)

        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                response = await client.get(source)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise InvalidKnowledgeSourceException(
                f"HTTP provider failed for source {source!r}: {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            raise InvalidKnowledgeSourceException(
                f"HTTP provider could not reach source {source!r}: {exc}"
            ) from exc

        content = self._extract_text(response)
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
            raise InvalidKnowledgeSourceException(
                "Invalid timeout configuration for HTTP provider"
            ) from exc

    def _extract_text(self, response: httpx.Response) -> str:
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                return json.dumps(response.json(), ensure_ascii=False, indent=2)
            except ValueError:
                return response.text
        return response.text
