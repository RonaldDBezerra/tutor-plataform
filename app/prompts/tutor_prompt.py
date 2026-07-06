"""Prompt builder for the TutorAgent."""

from __future__ import annotations

from app.knowledge.models import KnowledgeResult
from app.models.tutor import Tutor


def build_tutor_prompt(
    tutor: Tutor,
    contexts: list[KnowledgeResult],
    question: str,
) -> str:
    """Build the structured prompt consumed by the LLM."""

    context_blocks = [
        f"[provider={context.provider} source={context.source}]\n{context.content}"
        for context in contexts
    ]
    context_section = "\n\n".join(context_blocks) if context_blocks else ""

    return (
        f"SYSTEM:\n{tutor.instructions}\n\n"
        f"CONTEXT:\n{context_section}\n\n"
        f"USER:\n{question}"
    )
