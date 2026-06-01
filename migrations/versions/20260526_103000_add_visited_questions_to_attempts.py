"""Add visited question tracking to attempts

Revision ID: 20260526_103000
Revises: 20260525_214500
Create Date: 2026-05-26 10:30:00

"""

from alembic import op
import sqlalchemy as sa


revision = "20260526_103000"
down_revision = "20260525_214500"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("attempts")}

    if "visited_questions_json" not in existing_columns:
        op.add_column(
            "attempts",
            sa.Column(
                "visited_questions_json",
                sa.Text(),
                nullable=False,
                server_default="[]",
            ),
        )

    with op.batch_alter_table("attempts") as batch_op:
        if "visited_questions_json" not in existing_columns:
            batch_op.alter_column(
                "visited_questions_json",
                existing_type=sa.Text(),
                nullable=False,
                server_default=None,
            )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {column["name"] for column in inspector.get_columns("attempts")}

    with op.batch_alter_table("attempts") as batch_op:
        if "visited_questions_json" in existing_columns:
            batch_op.drop_column("visited_questions_json")
