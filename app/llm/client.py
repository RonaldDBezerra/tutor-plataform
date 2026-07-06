"""LangChain-backed LLM client."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings


class LLMClient:
    """Simple async client backed by LangChain's ChatOpenAI."""

    def __init__(
        self,
        *,
        model_name: str | None = None,
        temperature: float | None = None,
    ) -> None:
        self._model_name = model_name or settings.LLM_MODEL
        self._temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE

    def _build_model(self) -> ChatOpenAI:
        model_kwargs: dict[str, object] = {
            "model": self._model_name,
            "temperature": self._temperature,
        }
        if settings.OPENAI_API_KEY:
            model_kwargs["api_key"] = settings.OPENAI_API_KEY

        return ChatOpenAI(**model_kwargs)

    async def generate(self, prompt: str) -> str:
        """Generate a text response for a structured prompt."""

        response = await self._build_model().ainvoke([HumanMessage(content=prompt)])
        content = response.content

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            return "".join(str(item) for item in content)

        return str(content)
