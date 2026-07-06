"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import MessageRole, ProviderType, TutorStatus


class TutorBaseSchema(BaseModel):
    name: str = Field(..., min_length=1)
    description: str | None = None
    system_prompt: str = Field(..., min_length=1)
    status: TutorStatus


class TutorCreateRequest(TutorBaseSchema):
    pass


class TutorUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    status: TutorStatus | None = None


class TutorResponse(TutorBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class KnowledgeSourceCreateRequest(BaseModel):
    provider_type: ProviderType
    source_name: str = Field(..., min_length=1)
    source_url: str = Field(..., min_length=1)
    configuration: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class KnowledgeSourceUpdateRequest(BaseModel):
    provider_type: ProviderType | None = None
    source_name: str | None = None
    source_url: str | None = None
    configuration: dict[str, Any] | None = None
    enabled: bool | None = None


class KnowledgeSourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tutor_id: UUID
    provider_type: ProviderType
    source_name: str
    source_url: str
    configuration: dict[str, Any]
    enabled: bool
    created_at: datetime
    updated_at: datetime


class ConversationSourceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_name: str
    source_url: str
    provider_type: ProviderType


class ChatRequest(BaseModel):
    tutor_id: UUID
    conversation_id: str | None = None
    question: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: list[ConversationSourceSchema] = Field(default_factory=list)


class EmbedConfigResponse(BaseModel):
    tutor_id: UUID
    name: str
    description: str | None = None
    status: TutorStatus
    knowledge_sources_count: int
