"""Knowledge source attached to a tutor."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ProviderType

if TYPE_CHECKING:
    from app.models.tutor import Tutor


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tutor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tutors.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider_type: Mapped[ProviderType] = mapped_column(
        SAEnum(ProviderType, name="provider_type"),
        nullable=False,
    )
    source_name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    source_url: Mapped[str] = mapped_column(String(length=2048), nullable=False)
    configuration: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
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

    tutor: Mapped[Tutor] = relationship(back_populates="knowledge_sources")
