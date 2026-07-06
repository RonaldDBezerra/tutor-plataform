"""Prompt builder for the TutorAgent."""

from __future__ import annotations

from app.models.message import Message
from app.knowledge.models import KnowledgeResult
from app.models.tutor import Tutor


def _build_history_block(history: list[Message]) -> str:
    if not history:
        return ""

    lines: list[str] = []
    for message in history:
        lines.append(f"{message.role.value}: {message.content}")

    return "\n".join(lines)


def build_tutor_prompt(
    tutor: Tutor,
    contexts: list[KnowledgeResult],
    question: str,
    history: list[Message] | None = None,
) -> str:
    """Build the structured prompt consumed by the LLM."""

    context_blocks = [
        f"[provider={context.provider} source={context.source}]\n{context.content}"
        for context in contexts
    ]
    context_section = "\n\n".join(context_blocks) if context_blocks else ""
    history_section = _build_history_block(history or [])

    return (
        f"SYSTEM:\n{tutor.instructions}\n\n"
        f"HISTORY:\n{history_section}\n\n"
        f"CONTEXT:\n{context_section}\n\n"
        f"USER:\n{question}"
    )
