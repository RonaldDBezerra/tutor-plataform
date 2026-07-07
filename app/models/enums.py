"""Domain enums used by SQLAlchemy models."""

from enum import StrEnum


class TutorStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ProviderType(StrEnum):
    HTTP_TEXT = "HTTP_TEXT"
    JSON = "JSON"
    TAVILY_EXTRACT = "TAVILY_EXTRACT"


class MessageRole(StrEnum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"
