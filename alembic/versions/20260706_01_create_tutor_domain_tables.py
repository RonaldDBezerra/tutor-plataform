"""Create tutor domain tables.

Revision ID: 202607060001
Revises:
Create Date: 2026-07-06 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "202607060001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


tutor_status = postgresql.ENUM(
    "ACTIVE",
    "INACTIVE",
    name="tutor_status",
    create_type=False,
)
provider_type = postgresql.ENUM(
    "HTTP_TEXT",
    "JSON",
    "TAVILY_EXTRACT",
    name="provider_type",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    tutor_status.create(bind, checkfirst=True)
    provider_type.create(bind, checkfirst=True)

    op.create_table(
        "tutors",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("status", tutor_status, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tutors")),
    )
    op.create_table(
        "knowledge_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tutor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider_type", provider_type, nullable=False),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("source_url", sa.String(length=2048), nullable=False),
        sa.Column("configuration", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tutor_id"],
            ["tutors.id"],
            name=op.f("fk_knowledge_sources_tutor_id_tutors"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_sources")),
    )


def downgrade() -> None:
    op.drop_table("knowledge_sources")
    op.drop_table("tutors")

    bind = op.get_bind()
    provider_type.drop(bind, checkfirst=True)
    tutor_status.drop(bind, checkfirst=True)
