"""Chat endpoints."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends
from langsmith import traceable

from app.api.dependencies import get_chat_service, get_tutor_agent
from app.api.schemas import ChatRequest, ChatResponse, ConversationSourceSchema
from app.core.exceptions import TutorNotFoundError
from app.models.tutor import Tutor
from app.services.chat_service import ChatService
from app.agents.tutor_agent import TutorAgent

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


def _build_sources(tutor: Tutor | None) -> list[ConversationSourceSchema]:
    if tutor is None:
        return []

    sources = getattr(tutor, "knowledge_sources", [])
    return [ConversationSourceSchema.model_validate(source) for source in sources]


@traceable(name="chat_flow")
async def run_chat_flow(
    *,
    chat_service: ChatService,
    tutor_agent: TutorAgent,
    tutor_id: uuid.UUID,
    question: str,
    conversation_id: str | None = None,
) -> ChatResponse:
    tutor = await chat_service.get_tutor(tutor_id)
    if tutor is None:
        raise TutorNotFoundError(tutor_id)

    session_id = conversation_id or str(uuid.uuid4())
    conversation = await chat_service.get_or_create_conversation(
        tutor_id=tutor_id,
        session_id=session_id,
    )

    history = await chat_service.get_conversation_history(conversation.id)

    await chat_service.save_user_message(
        conversation_id=conversation.id,
        content=question,
    )

    answer = await tutor_agent.run(tutor=tutor, question=question, history=history)

    await chat_service.save_assistant_message(
        conversation_id=conversation.id,
        content=answer,
    )

    return ChatResponse(
        conversation_id=conversation.session_id,
        answer=answer,
        sources=_build_sources(tutor),
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(
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
