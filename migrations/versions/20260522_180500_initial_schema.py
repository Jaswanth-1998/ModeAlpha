"""Initial schema

Revision ID: 20260522_180500
Revises:
Create Date: 2026-05-22 18:05:00

"""
from alembic import op
import sqlalchemy as sa


revision = "20260522_180500"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    existing_tables = set(sa.inspect(op.get_bind()).get_table_names())

    if "users" not in existing_tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("username", sa.String(length=80), nullable=False),
            sa.Column("email", sa.String(length=120), nullable=False),
            sa.Column("mobile_number", sa.String(length=20), nullable=False),
            sa.Column("date_of_birth", sa.Date(), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("role", sa.String(length=20), nullable=False),
            sa.Column("is_approved", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("email"),
            sa.UniqueConstraint("username"),
        )
        existing_tables.add("users")

    if "mock_tests" not in existing_tables:
        op.create_table(
            "mock_tests",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=150), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("time_limit_minutes", sa.Integer(), nullable=False),
            sa.Column("marks_per_question", sa.Float(), nullable=False),
            sa.Column("negative_marking_enabled", sa.Boolean(), nullable=False),
            sa.Column("negative_mark_value", sa.Float(), nullable=False),
            sa.Column("unanswered_negative_marking_enabled", sa.Boolean(), nullable=False),
            sa.Column("unanswered_negative_mark_value", sa.Float(), nullable=False),
            sa.Column("total_questions", sa.Integer(), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_by", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        existing_tables.add("mock_tests")

    if "questions" not in existing_tables:
        op.create_table(
            "questions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("mock_test_id", sa.Integer(), nullable=False),
            sa.Column("question_text", sa.Text(), nullable=False),
            sa.Column("option_a", sa.Text(), nullable=False),
            sa.Column("option_b", sa.Text(), nullable=False),
            sa.Column("option_c", sa.Text(), nullable=False),
            sa.Column("option_d", sa.Text(), nullable=False),
            sa.Column("correct_answer", sa.String(length=1), nullable=False),
            sa.Column("question_order", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["mock_test_id"], ["mock_tests.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        existing_tables.add("questions")

    if "attempts" not in existing_tables:
        op.create_table(
            "attempts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("mock_test_id", sa.Integer(), nullable=False),
            sa.Column("answers_json", sa.Text(), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("started_at", sa.DateTime(), nullable=False),
            sa.Column("submitted_at", sa.DateTime(), nullable=True),
            sa.Column("time_taken_seconds", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(["mock_test_id"], ["mock_tests.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        existing_tables.add("attempts")

    if "results" not in existing_tables:
        op.create_table(
            "results",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("attempt_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("mock_test_id", sa.Integer(), nullable=False),
            sa.Column("total_questions", sa.Integer(), nullable=False),
            sa.Column("correct_answers", sa.Integer(), nullable=False),
            sa.Column("wrong_answers", sa.Integer(), nullable=False),
            sa.Column("unanswered_answers", sa.Integer(), nullable=False),
            sa.Column("obtained_marks", sa.Float(), nullable=False),
            sa.Column("total_marks", sa.Float(), nullable=False),
            sa.Column("percentage", sa.Float(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["attempt_id"], ["attempts.id"]),
            sa.ForeignKeyConstraint(["mock_test_id"], ["mock_tests.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("attempt_id"),
        )


def downgrade():
    existing_tables = set(sa.inspect(op.get_bind()).get_table_names())

    if "results" in existing_tables:
        op.drop_table("results")
    if "attempts" in existing_tables:
        op.drop_table("attempts")
    if "questions" in existing_tables:
        op.drop_table("questions")
    if "mock_tests" in existing_tables:
        op.drop_table("mock_tests")
    if "users" in existing_tables:
        op.drop_table("users")
