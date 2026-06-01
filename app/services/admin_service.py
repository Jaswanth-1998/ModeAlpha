from datetime import datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import distinct, func, or_
from werkzeug.utils import secure_filename

from app.config.settings import BaseConfig
from app.extensions import db
from app.models.attempt import Attempt
from app.models.mock_test import MockTest
from app.models.question import Question
from app.models.result import Result
from app.models.user import User
from app.services.docx_service import parse_questions_from_docx
from app.utils.helpers import parse_bool, parse_float, parse_int


def get_admin_dashboard_data():
    recent_results = (
        Result.query.join(User, User.id == Result.user_id)
        .join(MockTest, MockTest.id == Result.mock_test_id)
        .filter(User.role == "user", User.delete_flag == "N", MockTest.delete_flag == "N")
        .order_by(Result.created_at.desc())
        .all()
    )

    recent_activities = [
        {
            "username": result.user.username,
            "test_title": result.mock_test.title,
            "obtained_marks": result.obtained_marks,
            "percentage": round(result.percentage, 2),
            "submitted_at": result.created_at,
        }
        for result in recent_results
    ]

    return {
        "total_users": User.query.filter_by(role="user", delete_flag="N").count(),
        "total_tests": MockTest.query.filter_by(delete_flag="N").count(),
        "users_attended": db.session.query(func.count(distinct(Attempt.user_id)))
        .join(User, User.id == Attempt.user_id)
        .join(MockTest, MockTest.id == Attempt.mock_test_id)
        .filter(
            Attempt.status == "submitted",
            User.delete_flag == "N",
            MockTest.delete_flag == "N",
        )
        .scalar(),
        "pending_approvals": User.query.filter_by(
            role="user",
            is_approved=False,
            delete_flag="N",
        ).count(),
        "recent_activities": recent_activities,
    }


def get_pending_users():
    return (
        User.query.filter_by(role="user", is_approved=False, delete_flag="N")
        .order_by(User.created_at.asc())
        .all()
    )


def approve_user_account(user_id):
    user = User.query.filter_by(id=user_id, role="user", delete_flag="N").first()
    if not user:
        raise ValueError("User not found.")
    if user.is_approved:
        raise ValueError("This user is already approved.")

    user.is_approved = True
    user.is_active = True
    db.session.commit()
    return user


def get_tests_for_admin():
    return (
        MockTest.query.filter_by(delete_flag="N")
        .order_by(MockTest.created_at.desc())
        .all()
    )


def get_mock_test_by_id(test_id, include_deleted=False):
    query = MockTest.query.filter_by(id=test_id)
    if not include_deleted:
        query = query.filter_by(delete_flag="N")
    test = query.first()
    if not test:
        raise ValueError("Mock test not found.")
    return test


def create_mock_test(form_data, admin_id):
    mock_test = MockTest(created_by=admin_id, delete_flag="N")
    _apply_test_form_data(mock_test, form_data)
    db.session.add(mock_test)
    db.session.commit()
    return mock_test


def update_mock_test(mock_test, form_data):
    _apply_test_form_data(mock_test, form_data)
    db.session.commit()
    return mock_test


def delete_mock_test(test_id):
    test = get_mock_test_by_id(test_id)
    test.delete_flag = "Y"
    test.deleted_at = datetime.utcnow()
    test.is_active = False
    db.session.commit()


def search_users_for_settings(keyword):
    query = User.query.filter(User.role == "user")
    cleaned_keyword = (keyword or "").strip()

    if cleaned_keyword:
        like_value = f"%{cleaned_keyword}%"
        filters = [
            User.username.ilike(like_value),
            User.email.ilike(like_value),
            User.mobile_number.ilike(like_value),
        ]
        if cleaned_keyword.isdigit():
            filters.append(User.id == int(cleaned_keyword))
        query = query.filter(or_(*filters))

    return query.order_by(User.delete_flag.asc(), User.username.asc()).all()


def set_user_active_state(user_id, is_active):
    user = User.query.filter_by(id=user_id, role="user").first()
    if not user:
        raise ValueError("User not found.")
    if user.delete_flag == "Y":
        raise ValueError("Deleted users cannot be activated or deactivated.")

    user.is_active = is_active
    db.session.commit()
    return user


def soft_delete_user(user_id):
    user = User.query.filter_by(id=user_id, role="user").first()
    if not user:
        raise ValueError("User not found.")
    if user.delete_flag == "Y":
        raise ValueError("This user is already deleted.")

    user.delete_flag = "Y"
    user.deleted_at = datetime.utcnow()
    user.is_active = False
    db.session.commit()
    return user


def import_questions_for_test(mock_test, file_storage):
    if not file_storage or not file_storage.filename:
        raise ValueError("Please choose a .docx file to upload.")

    filename = secure_filename(file_storage.filename)
    if not filename.lower().endswith(".docx"):
        raise ValueError("Only .docx files are supported for question import.")

    upload_name = f"{uuid4().hex}_{filename}"
    upload_path = Path(BaseConfig.UPLOAD_DIR) / upload_name
    file_storage.save(upload_path)

    parsed_questions = parse_questions_from_docx(upload_path)

    Question.query.filter_by(mock_test_id=mock_test.id).delete()
    db.session.flush()

    for index, question_data in enumerate(parsed_questions, start=1):
        question = Question(
            mock_test_id=mock_test.id,
            question_order=index,
            **question_data,
        )
        db.session.add(question)

    mock_test.total_questions = len(parsed_questions)
    mock_test.updated_at = datetime.utcnow()
    db.session.commit()
    return len(parsed_questions)


def _apply_test_form_data(mock_test, form_data):
    title = (form_data.get("title") or "").strip()
    description = (form_data.get("description") or "").strip()

    if not title or not description:
        raise ValueError("Title and description are required.")

    time_limit_minutes = parse_int(form_data.get("time_limit_minutes"), "Time limit")
    marks_per_question = parse_float(form_data.get("marks_per_question"), "Marks per question")
    negative_enabled = parse_bool(form_data.get("negative_marking_enabled"))
    unanswered_negative_enabled = parse_bool(
        form_data.get("unanswered_negative_marking_enabled")
    )
    negative_mark_value = (
        parse_float(form_data.get("negative_mark_value"), "Negative mark value")
        if negative_enabled
        else 0.0
    )
    unanswered_negative_mark_value = (
        parse_float(
            form_data.get("unanswered_negative_mark_value"),
            "Unanswered negative mark value",
        )
        if unanswered_negative_enabled
        else 0.0
    )

    if time_limit_minutes <= 0:
        raise ValueError("Time limit must be greater than zero.")
    if marks_per_question <= 0:
        raise ValueError("Marks per question must be greater than zero.")

    mock_test.title = title
    mock_test.description = description
    mock_test.time_limit_minutes = time_limit_minutes
    mock_test.marks_per_question = marks_per_question
    mock_test.negative_marking_enabled = negative_enabled
    mock_test.negative_mark_value = negative_mark_value
    mock_test.unanswered_negative_marking_enabled = unanswered_negative_enabled
    mock_test.unanswered_negative_mark_value = unanswered_negative_mark_value
    mock_test.is_active = parse_bool(form_data.get("is_active"))
