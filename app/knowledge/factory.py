"""Factory for knowledge providers."""

from __future__ import annotations

from app.knowledge.exceptions import ProviderNotFoundException
from app.knowledge.interfaces import KnowledgeProvider
from app.knowledge.providers.http_provider import HttpProvider
from app.knowledge.providers.json_provider import JsonProvider
from app.knowledge.providers.tavily_provider import TavilyProvider
from app.models.enums import ProviderType


class KnowledgeProviderFactory:
    """Instantiate providers using a direct enum-to-class mapping."""

    _providers: dict[ProviderType, type[KnowledgeProvider]] = {
        ProviderType.HTTP_TEXT: HttpProvider,
        ProviderType.JSON: JsonProvider,
        ProviderType.TAVILY_EXTRACT: TavilyProvider,
    }

    @classmethod
    def create(cls, provider_type: ProviderType) -> KnowledgeProvider:
        provider_class = cls._providers.get(provider_type)
        if provider_class is None:
            raise ProviderNotFoundException(f"No provider registered for {provider_type!r}")
        return provider_class()
