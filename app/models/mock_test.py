from datetime import datetime

from app.extensions import db


class MockTest(db.Model):
    __tablename__ = "mock_tests"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    time_limit_minutes = db.Column(db.Integer, nullable=False)
    marks_per_question = db.Column(db.Float, nullable=False, default=1.0)
    negative_marking_enabled = db.Column(db.Boolean, nullable=False, default=False)
    negative_mark_value = db.Column(db.Float, nullable=False, default=0.0)
    unanswered_negative_marking_enabled = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )
    unanswered_negative_mark_value = db.Column(
        db.Float,
        nullable=False,
        default=0.0,
    )
    delete_flag = db.Column(db.String(1), default="N", nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    total_questions = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    creator = db.relationship("User", back_populates="created_tests")
    questions = db.relationship(
        "Question",
        back_populates="mock_test",
        order_by="Question.question_order",
        cascade="all, delete-orphan",
        lazy=True,
    )
    attempts = db.relationship(
        "Attempt",
        back_populates="mock_test",
        cascade="all, delete-orphan",
        lazy=True,
    )
    results = db.relationship(
        "Result",
        back_populates="mock_test",
        cascade="all, delete-orphan",
        lazy=True,
    )

    def __repr__(self):
        return f"<MockTest {self.title}>"
