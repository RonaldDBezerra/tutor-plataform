"""Exceptions for the knowledge abstraction layer."""


class KnowledgeLayerException(Exception):
    """Base exception for knowledge layer errors."""


class ProviderNotFoundException(KnowledgeLayerException):
    """Raised when a provider type is not mapped in the factory."""


class ProviderNotImplementedException(KnowledgeLayerException):
    """Raised when a provider exists structurally but is not implemented yet."""


class InvalidKnowledgeSourceException(KnowledgeLayerException):
    """Raised when a source or response is invalid for knowledge extraction."""
