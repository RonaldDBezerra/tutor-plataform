"""Tavily knowledge provider."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Mapping

from langchain_tavily import TavilyExtract

from app.core.config import settings
from app.knowledge.exceptions import InvalidKnowledgeSourceException
from app.knowledge.interfaces import KnowledgeProvider
from app.knowledge.models import KnowledgeResult

logger = logging.getLogger(__name__)


class TavilyProvider(KnowledgeProvider):
    """Extract web content through Tavily's official LangChain integration."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_base_url: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.api_base_url = api_base_url or settings.TAVILY_API_BASE_URL
        self.timeout_seconds = (
            timeout_seconds if timeout_seconds is not None else settings.TAVILY_TIMEOUT_SECONDS
        )

    async def validate(self, source: str, configuration: dict | None = None) -> None:
        await self._extract(source=source, configuration=configuration)

    async def get_context(
        self,
        source: str,
        question: str | None = None,
        configuration: dict | None = None,
    ) -> KnowledgeResult:
        payload = await self._extract(source=source, configuration=configuration)
        results = payload.get("results", [])

        if not results:
            raise InvalidKnowledgeSourceException(
                f"Tavily provider returned no extracted content for {source!r}"
            )

        content_blocks = [
            result.get("raw_content", "")
            for result in results
            if isinstance(result, Mapping) and result.get("raw_content")
        ]
        content = "\n\n".join(content_blocks).strip()
        if not content:
            raise InvalidKnowledgeSourceException(
                f"Tavily provider returned empty content for {source!r}"
            )

        metadata = {
            "question": question,
            "response_time": payload.get("response_time"),
            "failed_results": payload.get("failed_results", []),
            "results_count": len(results),
        }
        return KnowledgeResult(
            content=content,
            metadata=metadata,
            provider=self.__class__.__name__,
            source=source,
        )

    def _build_tool(self, configuration: dict | None = None) -> TavilyExtract:
        configuration = configuration or {}

        tool_kwargs: dict[str, object] = {}
        if self.api_key:
            tool_kwargs["tavily_api_key"] = self.api_key
        if self.api_base_url:
            tool_kwargs["api_base_url"] = self.api_base_url

        for key in (
            "extract_depth",
            "include_images",
            "include_favicon",
            "format",
            "include_usage",
            "query",
            "chunks_per_source",
        ):
            if key in configuration and configuration[key] is not None:
                tool_kwargs[key] = configuration[key]

        return TavilyExtract(**tool_kwargs)

    async def _extract(self, source: str, configuration: dict | None = None) -> dict[str, object]:
        if not source.strip():
            raise InvalidKnowledgeSourceException("Tavily provider requires a non-empty source URL")

        if not self.api_key:
            raise InvalidKnowledgeSourceException("TAVILY_API_KEY is required for Tavily provider")

        tool = self._build_tool(configuration)
        extract_depth = (configuration or {}).get("extract_depth", "basic")
        include_images = (configuration or {}).get("include_images", False)

        try:
            raw_results = await asyncio.wait_for(
                tool.ainvoke(
                    {
                        "urls": [source],
                        "extract_depth": extract_depth,
                        "include_images": include_images,
                    }
                ),
                timeout=self.timeout_seconds,
            )
        except asyncio.TimeoutError as exc:
            logger.exception("Tavily provider timed out for source=%s", source)
            raise InvalidKnowledgeSourceException(
                f"Tavily provider timed out after {self.timeout_seconds} seconds "
                f"for source {source!r}"
            ) from exc
        except Exception as exc:
            logger.exception("Tavily provider failed for source=%s", source)
            raise InvalidKnowledgeSourceException(
                f"Tavily provider failed for source {source!r}: {exc}"
            ) from exc

        if not isinstance(raw_results, Mapping):
            raise InvalidKnowledgeSourceException(
                f"Tavily provider returned an invalid payload for {source!r}"
            )

        return dict(raw_results)
