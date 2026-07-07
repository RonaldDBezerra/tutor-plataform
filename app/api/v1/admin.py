"""Administrative endpoints for tutors and knowledge sources."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.api.dependencies import get_knowledge_service, get_tutor_service
from app.api.schemas import (
    KnowledgeSourceCreateRequest,
    KnowledgeSourceResponse,
    KnowledgeSourceUpdateRequest,
    TutorCreateRequest,
    TutorResponse,
    TutorUpdateRequest,
)
from app.core.exceptions import KnowledgeSourceNotFoundError, TutorNotFoundError
from app.core.security import require_admin_api_key
from app.models.enums import TutorStatus
from app.services.knowledge_service import KnowledgeService
from app.services.tutor_service import TutorService

router = APIRouter(tags=["admin"])
protected_router = APIRouter(tags=["admin"], dependencies=[Depends(require_admin_api_key)])

ADMIN_AUTH_DESCRIPTION = "Requires the X-ADMIN-KEY header with a valid admin API key."


@protected_router.post(
    "/tutors",
    response_model=TutorResponse,
    status_code=status.HTTP_201_CREATED,
    description=ADMIN_AUTH_DESCRIPTION,
)
async def create_tutor(
    request: TutorCreateRequest,
    tutor_service: TutorService = Depends(get_tutor_service),
) -> TutorResponse:
    tutor = await tutor_service.create(
        name=request.name,
        description=request.description,
        system_prompt=request.system_prompt,
        status=request.status,
    )
    return TutorResponse.model_validate(tutor)


@router.get("/tutors", response_model=list[TutorResponse])
async def list_tutors(
    tutor_service: TutorService = Depends(get_tutor_service),
) -> list[TutorResponse]:
    tutors = await tutor_service.list()
    return [TutorResponse.model_validate(tutor) for tutor in tutors]


@router.get("/tutors/{tutor_id}", response_model=TutorResponse)
async def get_tutor(
    tutor_id: UUID,
    tutor_service: TutorService = Depends(get_tutor_service),
) -> TutorResponse:
    tutor = await tutor_service.get_by_id(tutor_id)
    if tutor is None:
        raise TutorNotFoundError(tutor_id)

    return TutorResponse.model_validate(tutor)


@protected_router.patch(
    "/tutors/{tutor_id}",
    response_model=TutorResponse,
    description=ADMIN_AUTH_DESCRIPTION,
)
async def update_tutor(
    tutor_id: UUID,
    request: TutorUpdateRequest,
    tutor_service: TutorService = Depends(get_tutor_service),
) -> TutorResponse:
    tutor = await tutor_service.update(
        tutor_id,
        name=request.name,
        description=request.description,
        system_prompt=request.system_prompt,
        status=request.status,
    )
    return TutorResponse.model_validate(tutor)


@protected_router.delete(
    "/tutors/{tutor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description=ADMIN_AUTH_DESCRIPTION,
)
async def delete_tutor(
    tutor_id: UUID,
    tutor_service: TutorService = Depends(get_tutor_service),
) -> Response:
    await tutor_service.delete(tutor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@protected_router.post(
    "/tutors/{tutor_id}/knowledge-sources",
    response_model=KnowledgeSourceResponse,
    status_code=status.HTTP_201_CREATED,
    description=ADMIN_AUTH_DESCRIPTION,
)
async def create_knowledge_source(
    tutor_id: UUID,
    request: KnowledgeSourceCreateRequest,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> KnowledgeSourceResponse:
    knowledge_source = await knowledge_service.create(
        tutor_id=tutor_id,
        provider_type=request.provider_type,
        source_name=request.source_name,
        source_url=request.source_url,
        configuration=request.configuration,
        enabled=request.enabled,
    )
    return KnowledgeSourceResponse.model_validate(knowledge_source)


@router.get("/tutors/{tutor_id}/knowledge-sources", response_model=list[KnowledgeSourceResponse])
async def list_knowledge_sources(
    tutor_id: UUID,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> list[KnowledgeSourceResponse]:
    knowledge_sources = await knowledge_service.list_by_tutor(tutor_id)
    return [KnowledgeSourceResponse.model_validate(item) for item in knowledge_sources]


@protected_router.patch(
    "/knowledge-sources/{knowledge_source_id}",
    response_model=KnowledgeSourceResponse,
    description=ADMIN_AUTH_DESCRIPTION,
)
async def update_knowledge_source(
    knowledge_source_id: UUID,
    request: KnowledgeSourceUpdateRequest,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> KnowledgeSourceResponse:
    knowledge_source = await knowledge_service.update(
        knowledge_source_id,
        provider_type=request.provider_type,
        source_name=request.source_name,
        source_url=request.source_url,
        configuration=request.configuration,
        enabled=request.enabled,
    )
    return KnowledgeSourceResponse.model_validate(knowledge_source)


@protected_router.delete(
    "/knowledge-sources/{knowledge_source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description=ADMIN_AUTH_DESCRIPTION,
)
async def delete_knowledge_source(
    knowledge_source_id: UUID,
    knowledge_service: KnowledgeService = Depends(get_knowledge_service),
) -> Response:
    await knowledge_service.delete(knowledge_source_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


router.include_router(protected_router)
