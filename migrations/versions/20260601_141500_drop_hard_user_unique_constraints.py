"""Drop hard user unique constraints for soft-delete aware registration

Revision ID: 20260601_141500
Revises: 20260526_103000
Create Date: 2026-06-01 14:15:00

"""
from alembic import op
import sqlalchemy as sa


revision = "20260601_141500"
down_revision = "20260526_103000"
branch_labels = None
depends_on = None


def _drop_unique_constraint_by_columns(table_name, column_names):
    inspector = sa.inspect(op.get_bind())
    for constraint in inspector.get_unique_constraints(table_name):
        if constraint.get("column_names") == list(column_names) and constraint.get("name"):
            op.drop_constraint(constraint["name"], table_name, type_="unique")
            break


def _has_unique_constraint(table_name, column_names):
    inspector = sa.inspect(op.get_bind())
    return any(
        constraint.get("column_names") == list(column_names)
        for constraint in inspector.get_unique_constraints(table_name)
    )


def upgrade():
    _drop_unique_constraint_by_columns("users", ["email"])
    _drop_unique_constraint_by_columns("users", ["username"])


def downgrade():
    if not _has_unique_constraint("users", ["username"]):
        op.create_unique_constraint("uq_users_username", "users", ["username"])
    if not _has_unique_constraint("users", ["email"]):
        op.create_unique_constraint("uq_users_email", "users", ["email"])
