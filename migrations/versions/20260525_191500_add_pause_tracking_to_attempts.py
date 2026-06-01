"""Add pause tracking fields to attempts

Revision ID: 20260525_191500
Revises: 20260522_180500
Create Date: 2026-05-25 19:15:00

"""

from alembic import op
import sqlalchemy as sa


revision = "20260525_191500"
down_revision = "20260522_180500"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("attempts")}

    if "last_resumed_at" not in existing_columns:
        op.add_column("attempts", sa.Column("last_resumed_at", sa.DateTime(), nullable=True))
    if "paused_at" not in existing_columns:
        op.add_column("attempts", sa.Column("paused_at", sa.DateTime(), nullable=True))
    if "elapsed_seconds" not in existing_columns:
        op.add_column(
            "attempts",
            sa.Column("elapsed_seconds", sa.Integer(), nullable=False, server_default="0"),
        )

    attempts = sa.table(
        "attempts",
        sa.column("id", sa.Integer()),
        sa.column("started_at", sa.DateTime()),
        sa.column("last_resumed_at", sa.DateTime()),
    )

    bind.execute(
        attempts.update()
        .where(attempts.c.last_resumed_at.is_(None))
        .values(last_resumed_at=attempts.c.started_at)
    )

    with op.batch_alter_table("attempts") as batch_op:
        batch_op.alter_column("last_resumed_at", existing_type=sa.DateTime(), nullable=False)
        batch_op.alter_column(
            "elapsed_seconds",
            existing_type=sa.Integer(),
            nullable=False,
            server_default=None,
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("attempts")}

    with op.batch_alter_table("attempts") as batch_op:
        if "elapsed_seconds" in existing_columns:
            batch_op.drop_column("elapsed_seconds")
        if "paused_at" in existing_columns:
            batch_op.drop_column("paused_at")
        if "last_resumed_at" in existing_columns:
            batch_op.drop_column("last_resumed_at")
