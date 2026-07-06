"""Tutor aggregate root."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import TutorStatus


class Tutor(Base):
    __tablename__ = "tutors"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    system_prompt: Mapped[str] = mapped_column(Text(), nullable=False)
    status: Mapped[TutorStatus] = mapped_column(
        SAEnum(TutorStatus, name="tutor_status"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    knowledge_sources: Mapped[list["KnowledgeSource"]] = relationship(
        back_populates="tutor",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def instructions(self) -> str:
        """Compatibility alias used by the agent prompt builder."""

        return self.system_prompt