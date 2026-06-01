"""Add soft delete flags and user active status

Revision ID: 20260525_214500
Revises: 20260525_191500
Create Date: 2026-05-25 21:45:00

"""

from alembic import op
import sqlalchemy as sa


revision = "20260525_214500"
down_revision = "20260525_191500"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    test_columns = {column["name"] for column in inspector.get_columns("mock_tests")}

    if "is_active" not in user_columns:
        op.add_column(
            "users",
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        )
    if "delete_flag" not in user_columns:
        op.add_column(
            "users",
            sa.Column("delete_flag", sa.String(length=1), nullable=False, server_default="N"),
        )
    if "deleted_at" not in user_columns:
        op.add_column("users", sa.Column("deleted_at", sa.DateTime(), nullable=True))

    if "delete_flag" not in test_columns:
        op.add_column(
            "mock_tests",
            sa.Column("delete_flag", sa.String(length=1), nullable=False, server_default="N"),
        )
    if "deleted_at" not in test_columns:
        op.add_column("mock_tests", sa.Column("deleted_at", sa.DateTime(), nullable=True))

    with op.batch_alter_table("users") as batch_op:
        if "is_active" not in user_columns:
            batch_op.alter_column("is_active", existing_type=sa.Boolean(), nullable=False, server_default=None)
        if "delete_flag" not in user_columns:
            batch_op.alter_column("delete_flag", existing_type=sa.String(length=1), nullable=False, server_default=None)

    with op.batch_alter_table("mock_tests") as batch_op:
        if "delete_flag" not in test_columns:
            batch_op.alter_column("delete_flag", existing_type=sa.String(length=1), nullable=False, server_default=None)


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    user_columns = {column["name"] for column in inspector.get_columns("users")}
    test_columns = {column["name"] for column in inspector.get_columns("mock_tests")}

    with op.batch_alter_table("mock_tests") as batch_op:
        if "deleted_at" in test_columns:
            batch_op.drop_column("deleted_at")
        if "delete_flag" in test_columns:
            batch_op.drop_column("delete_flag")

    with op.batch_alter_table("users") as batch_op:
        if "deleted_at" in user_columns:
            batch_op.drop_column("deleted_at")
        if "delete_flag" in user_columns:
            batch_op.drop_column("delete_flag")
        if "is_active" in user_columns:
            batch_op.drop_column("is_active")
