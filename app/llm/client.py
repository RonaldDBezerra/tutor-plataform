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
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        self._model = ChatOpenAI(
            model=model_name or settings.LLM_MODEL,
            temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
        )

    async def generate(self, prompt: str) -> str:
        """Generate a text response for a structured prompt."""

        response = await self._model.ainvoke([HumanMessage(content=prompt)])
        content = response.content

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            return "".join(str(item) for item in content)

        return str(content)
