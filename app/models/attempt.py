from datetime import datetime

from app.extensions import db


class Attempt(db.Model):
    __tablename__ = "attempts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mock_test_id = db.Column(db.Integer, db.ForeignKey("mock_tests.id"), nullable=False)
    answers_json = db.Column(db.Text, nullable=False, default="{}")
    visited_questions_json = db.Column(db.Text, nullable=False, default="[]")
    status = db.Column(db.String(20), nullable=False, default="in_progress")
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_resumed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    paused_at = db.Column(db.DateTime, nullable=True)
    elapsed_seconds = db.Column(db.Integer, nullable=False, default=0)
    submitted_at = db.Column(db.DateTime, nullable=True)
    time_taken_seconds = db.Column(db.Integer, nullable=True)

    user = db.relationship("User", back_populates="attempts")
    mock_test = db.relationship("MockTest", back_populates="attempts")
    result = db.relationship(
        "Result",
        back_populates="attempt",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Attempt {self.id} user={self.user_id} test={self.mock_test_id}>"
