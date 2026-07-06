"""Dependency providers for API routes."""

from __future__ import annotations

from fastapi import Request

from app.agents.tutor_agent import TutorAgent
from app.db.uow import UnitOfWork
from app.llm.client import LLMClient
from app.services.chat_service import ChatService
from app.services.knowledge_service import KnowledgeService
from app.services.tutor_service import TutorService
from app.tools.knowledge_tool import KnowledgeTool


def get_tutor_service() -> TutorService:
    return TutorService(UnitOfWork())


def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService(UnitOfWork())


def get_chat_service() -> ChatService:
    return ChatService(UnitOfWork())


def get_knowledge_tool(request: Request) -> KnowledgeTool:
    return request.app.state.knowledge_tool


def get_llm_client(request: Request) -> LLMClient:
    return request.app.state.llm_client


def get_tutor_agent(request: Request) -> TutorAgent:
    return request.app.state.tutor_agent
