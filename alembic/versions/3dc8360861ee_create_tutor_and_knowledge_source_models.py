"""create tutor and knowledge source models

Revision ID: 3dc8360861ee
Revises: 202607060001
Create Date: 2026-07-06 13:53:29.057254

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3dc8360861ee"
down_revision: Union[str, Sequence[str], None] = "202607060001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    bind = op.get_bind()

    message_role = postgresql.ENUM(
        "USER",
        "ASSISTANT",
        "SYSTEM",
        name="message_role",
        create_type=False,
    )
    message_role.create(bind, checkfirst=True)

    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tutor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=False),
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
            name=op.f("fk_conversations_tutor_id_tutors"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_conversations")),
        sa.UniqueConstraint("tutor_id", "session_id", name="uq_conversations_tutor_id_session_id"),
    )
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", message_role, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            name=op.f("fk_messages_conversation_id_conversations"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_messages")),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("messages")
    op.drop_table("conversations")

    bind = op.get_bind()
    message_role = postgresql.ENUM(
        "USER",
        "ASSISTANT",
        "SYSTEM",
        name="message_role",
        create_type=False,
    )
    message_role.drop(bind, checkfirst=True)
