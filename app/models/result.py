from datetime import datetime

from app.extensions import db


class Result(db.Model):
    __tablename__ = "results"

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("attempts.id"), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    mock_test_id = db.Column(db.Integer, db.ForeignKey("mock_tests.id"), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False, default=0)
    wrong_answers = db.Column(db.Integer, nullable=False, default=0)
    unanswered_answers = db.Column(db.Integer, nullable=False, default=0)
    obtained_marks = db.Column(db.Float, nullable=False, default=0.0)
    total_marks = db.Column(db.Float, nullable=False, default=0.0)
    percentage = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    attempt = db.relationship("Attempt", back_populates="result")
    user = db.relationship("User", back_populates="results")
    mock_test = db.relationship("MockTest", back_populates="results")

    def __repr__(self):
        return f"<Result {self.id} attempt={self.attempt_id}>"
