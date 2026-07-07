"""Value objects returned by knowledge providers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class KnowledgeResult:
    """Normalized knowledge payload returned by every provider."""

    content: str
    metadata: dict[str, object] = field(default_factory=dict)
    provider: str = ""
    source: str = ""
