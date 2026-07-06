"""Abstraction for LLM backends."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Simple async interface used by the agent to generate text."""

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a text completion for the given prompt."""
