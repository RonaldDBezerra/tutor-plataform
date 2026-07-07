"""Add embed token to tutors.

Revision ID: 20260707_01
Revises: 3dc8360861ee
Create Date: 2026-07-07 00:00:00.000000
"""

from __future__ import annotations

from uuid import uuid4

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260707_01"
down_revision: str | None = "3dc8360861ee"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "tutors",
        sa.Column("embed_token", sa.String(length=32), nullable=True),
    )

    connection = op.get_bind()
    tutor_rows = connection.execute(sa.text("SELECT id FROM tutors")).all()
    for (tutor_id,) in tutor_rows:
        connection.execute(
            sa.text("UPDATE tutors SET embed_token = :embed_token WHERE id = :tutor_id"),
            {"embed_token": uuid4().hex, "tutor_id": tutor_id},
        )

    op.alter_column("tutors", "embed_token", nullable=False)
    op.create_index(op.f("ix_tutors_embed_token"), "tutors", ["embed_token"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_tutors_embed_token"), table_name="tutors")
    op.drop_column("tutors", "embed_token")
