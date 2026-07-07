"""Global exception handlers for the HTTP API."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    ApplicationError,
    ConversationNotFoundError,
    EmbedTokenNotFoundError,
    KnowledgeSourceNotFoundError,
    ResourceNotFoundError,
    TutorNotFoundError,
)
from app.knowledge.exceptions import (
    InvalidKnowledgeSourceException,
    ProviderNotFoundException,
    ProviderNotImplementedException,
)


def _build_error_payload(error_code: str, detail: str) -> dict[str, str]:
    return {"error": error_code, "detail": detail}


async def application_error_handler(_: Request, exc: ApplicationError) -> JSONResponse:
    if isinstance(exc, ResourceNotFoundError):
        status_code = 404
    else:
        status_code = 400

    if isinstance(exc, TutorNotFoundError):
        error_code = "tutor_not_found"
    elif isinstance(exc, EmbedTokenNotFoundError):
        error_code = "embed_token_not_found"
    elif isinstance(exc, KnowledgeSourceNotFoundError):
        error_code = "knowledge_source_not_found"
    elif isinstance(exc, ConversationNotFoundError):
        error_code = "conversation_not_found"
    else:
        error_code = "application_error"

    return JSONResponse(status_code=status_code, content=_build_error_payload(error_code, str(exc)))


async def knowledge_error_handler(_: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, ProviderNotImplementedException):
        status_code = 501
        error_code = "provider_not_implemented"
    elif isinstance(exc, ProviderNotFoundException):
        status_code = 400
        error_code = "provider_not_found"
    elif isinstance(exc, InvalidKnowledgeSourceException):
        status_code = 400
        error_code = "invalid_knowledge_source"
    else:
        status_code = 500
        error_code = "knowledge_error"

    return JSONResponse(status_code=status_code, content=_build_error_payload(error_code, str(exc)))


async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "detail": "Invalid request payload",
            "errors": exc.errors(),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(InvalidKnowledgeSourceException, knowledge_error_handler)
    app.add_exception_handler(ProviderNotFoundException, knowledge_error_handler)
    app.add_exception_handler(ProviderNotImplementedException, knowledge_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
