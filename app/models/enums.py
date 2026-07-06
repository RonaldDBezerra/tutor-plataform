"""Domain enums used by SQLAlchemy models."""

from enum import Enum


class TutorStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ProviderType(str, Enum):
    HTTP_TEXT = "HTTP_TEXT"
    JSON = "JSON"
    TAVILY_EXTRACT = "TAVILY_EXTRACT"