"""Application-level exceptions for API error handling."""

from __future__ import annotations


class ApplicationError(Exception):
    """Base class for application errors exposed through the API."""


class ResourceNotFoundError(ApplicationError):
    """Base class for not-found errors."""


class TutorNotFoundError(ResourceNotFoundError):
    """Raised when a tutor cannot be found."""

    def __init__(self, tutor_id: object) -> None:
        super().__init__(f"Tutor not found: {tutor_id}")
        self.tutor_id = tutor_id


class EmbedTokenNotFoundError(ResourceNotFoundError):
    """Raised when an embed token cannot be resolved to a tutor."""

    def __init__(self, embed_token: object) -> None:
        super().__init__(f"Embed token not found: {embed_token}")
        self.embed_token = embed_token


class KnowledgeSourceNotFoundError(ResourceNotFoundError):
    """Raised when a knowledge source cannot be found."""

    def __init__(self, knowledge_source_id: object) -> None:
        super().__init__(f"Knowledge source not found: {knowledge_source_id}")
        self.knowledge_source_id = knowledge_source_id


class ConversationNotFoundError(ResourceNotFoundError):
    """Raised when a conversation cannot be found."""

    def __init__(self, conversation_id: object) -> None:
        super().__init__(f"Conversation not found: {conversation_id}")
        self.conversation_id = conversation_id
