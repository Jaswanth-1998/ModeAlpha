from datetime import datetime

from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile_number = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    delete_flag = db.Column(db.String(1), default="N", nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    attempts = db.relationship(
        "Attempt",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True,
    )
    results = db.relationship(
        "Result",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy=True,
    )
    created_tests = db.relationship("MockTest", back_populates="creator", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"
