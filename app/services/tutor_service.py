"""Tutor application service."""

from __future__ import annotations

import uuid

from app.core.exceptions import TutorNotFoundError
from app.db.uow import UnitOfWork
from app.models.enums import TutorStatus
from app.models.tutor import Tutor


class TutorService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def create(
        self,
        *,
        name: str,
        description: str | None,
        system_prompt: str,
        status: TutorStatus,
    ) -> Tutor:
        async with self.uow:
            tutor = Tutor(
                name=name,
                description=description,
                system_prompt=system_prompt,
                status=status,
            )
            created_tutor = await self.uow.tutors.create(tutor)
            await self.uow.commit()
            return created_tutor

    async def get_by_id(self, tutor_id: uuid.UUID) -> Tutor | None:
        async with self.uow:
            return await self.uow.tutors.get_by_id(tutor_id)

    async def list(self, *, status: TutorStatus | None = None) -> list[Tutor]:
        async with self.uow:
            tutors = await self.uow.tutors.list(status=status)
            return list(tutors)

    async def update(
        self,
        tutor_id: uuid.UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        system_prompt: str | None = None,
        status: TutorStatus | None = None,
    ) -> Tutor | None:
        async with self.uow:
            tutor = await self.uow.tutors.get_by_id(tutor_id)
            if tutor is None:
                raise TutorNotFoundError(tutor_id)

            if name is not None:
                tutor.name = name
            if description is not None:
                tutor.description = description
            if system_prompt is not None:
                tutor.system_prompt = system_prompt
            if status is not None:
                tutor.status = status

            updated_tutor = await self.uow.tutors.update(tutor)
            await self.uow.commit()
            return updated_tutor

    async def deactivate(self, tutor_id: uuid.UUID) -> Tutor | None:
        async with self.uow:
            tutor = await self.uow.tutors.get_by_id(tutor_id)
            if tutor is None:
                raise TutorNotFoundError(tutor_id)

            deactivated_tutor = await self.uow.tutors.deactivate(tutor)
            await self.uow.commit()
            return deactivated_tutor

    async def delete(self, tutor_id: uuid.UUID) -> Tutor | None:
        return await self.deactivate(tutor_id)
