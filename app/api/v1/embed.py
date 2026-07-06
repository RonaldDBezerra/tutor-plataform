"""Embed-ready endpoints reusing the chat orchestration."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends

from app.api.dependencies import get_chat_service, get_tutor_agent, get_tutor_service
from app.api.schemas import ChatRequest, ChatResponse, EmbedConfigResponse
from app.api.v1.chat import run_chat_flow
from app.core.exceptions import TutorNotFoundError
from app.services.chat_service import ChatService
from app.services.tutor_service import TutorService
from app.agents.tutor_agent import TutorAgent

router = APIRouter(tags=["embed"])


@router.get("/embed/{tutor_id}/config", response_model=EmbedConfigResponse)
async def get_embed_config(
    tutor_id: uuid.UUID,
    tutor_service: TutorService = Depends(get_tutor_service),
) -> EmbedConfigResponse:
    tutor = await tutor_service.get_by_id(tutor_id)
    if tutor is None:
        raise TutorNotFoundError(tutor_id)

    return EmbedConfigResponse(
        tutor_id=tutor.id,
        name=tutor.name,
        description=tutor.description,
        status=tutor.status,
        knowledge_sources_count=len(tutor.knowledge_sources),
    )


@router.post("/embed/chat", response_model=ChatResponse)
async def embed_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
    tutor_agent: TutorAgent = Depends(get_tutor_agent),
) -> ChatResponse:
    return await run_chat_flow(
        chat_service=chat_service,
        tutor_agent=tutor_agent,
        tutor_id=request.tutor_id,
        question=request.question,
        conversation_id=request.conversation_id,
    )
