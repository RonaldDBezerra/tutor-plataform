"""FastAPI application entrypoint for the Tutor Platform."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agents.tutor_agent import TutorAgent
from app.api.errors import register_exception_handlers
from app.api.v1 import router as api_v1_router
from app.llm.client import LLMClient
from app.tools.knowledge_tool import KnowledgeTool


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.knowledge_tool = KnowledgeTool()
    app.state.llm_client = LLMClient()
    app.state.tutor_agent = TutorAgent(app.state.knowledge_tool, app.state.llm_client)
    yield


app = FastAPI(title="Tutor Platform", lifespan=lifespan)
register_exception_handlers(app)
app.include_router(api_v1_router)
