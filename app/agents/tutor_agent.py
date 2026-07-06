"""Tutor agent orchestration."""

from __future__ import annotations

import logging

from app.knowledge.models import KnowledgeResult
from app.models.message import Message
from app.models.tutor import Tutor
from app.prompts.tutor_prompt import build_tutor_prompt
from app.tools.knowledge_tool import KnowledgeTool
from app.llm.client import LLMClient

logger = logging.getLogger(__name__)


class TutorAgent:
    """Orchestrates knowledge retrieval, prompt construction and LLM calls."""

    def __init__(self, knowledge_tool: KnowledgeTool, llm_client: LLMClient) -> None:
        self.knowledge_tool = knowledge_tool
        self.llm_client = llm_client

    async def run(
        self,
        tutor: Tutor,
        question: str,
        history: list[Message] | None = None,
    ) -> str:
        try:
            contexts: list[KnowledgeResult] = await self.knowledge_tool.get_contexts(
                list(tutor.knowledge_sources),
                question=question,
            )
            prompt = build_tutor_prompt(tutor, contexts, question, history=history)
            return await self.llm_client.generate(prompt)
        except Exception:
            logger.exception("TutorAgent failed for tutor_id=%s", tutor.id)
            raise