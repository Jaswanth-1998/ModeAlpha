from sqlalchemy import func, or_

from app.models.attempt import Attempt
from app.models.mock_test import MockTest
from app.models.result import Result
from app.models.user import User
from app.utils.helpers import build_result_attempt_map


def _not_deleted(model):
    return or_(model.delete_flag == "N", model.delete_flag.is_(None))


def get_user_dashboard_data(user_id):
    total_available_tests = (
        MockTest.query.filter(
            MockTest.is_active.is_(True),
            MockTest.total_questions > 0,
            _not_deleted(MockTest),
        )
        .count()
    )
    results = (
        Result.query.filter_by(user_id=user_id)
        .order_by(Result.created_at.desc(), Result.id.desc())
        .all()
    )
    attended_tests = len(results)
    average_marks = round(
        sum(result.obtained_marks for result in results) / attended_tests,
        2,
    ) if attended_tests else 0

    return {
        "total_available_tests": total_available_tests,
        "attended_tests": attended_tests,
        "recent_results": results,
        "latest_result": results[0] if results else None,
        "average_marks": average_marks,
    }


def get_admin_reports():
    users = (
        User.query.filter(User.role == "user", _not_deleted(User))
        .order_by(User.username.asc())
        .all()
    )
    approved_users = [user for user in users if user.is_approved]
    tests = (
        MockTest.query.filter(_not_deleted(MockTest))
        .order_by(MockTest.title.asc())
        .all()
    )

    user_report = []
    for user in users:
        user_results = (
            Result.query.filter_by(user_id=user.id)
            .order_by(Result.created_at.desc(), Result.id.desc())
            .all()
        )
        attempts_count = len(user_results)
        total_marks = round(sum(result.obtained_marks for result in user_results), 2)
        average_percentage = round(
            sum(result.percentage for result in user_results) / attempts_count,
            2,
        ) if attempts_count else 0
        user_report.append(
            {
                "user": user,
                "tests_attended_count": attempts_count,
                "total_marks": total_marks,
                "percentage": average_percentage,
            }
        )

    test_report = []
    for test in tests:
        test_results = (
            Result.query.join(User, User.id == Result.user_id)
            .filter(Result.mock_test_id == test.id, _not_deleted(User))
            .order_by(Result.created_at.desc(), Result.id.desc())
            .all()
        )
        attempts_count = len(test_results)
        unique_users_attended = len({result.user_id for result in test_results})
        highest_score = max(
            (result.obtained_marks for result in test_results),
            default=0,
        )
        test_report.append(
            {
                "test": test,
                "total_marks": round(test.total_questions * test.marks_per_question, 2),
                "attempts_count": attempts_count,
                "users_attended_count": unique_users_attended,
                "highest_score": highest_score,
            }
        )

    overall_metrics = {
        "approved_users": User.query.filter(
            User.role == "user",
            User.is_approved.is_(True),
            _not_deleted(User),
        ).count(),
        "pending_users": User.query.filter(
            User.role == "user",
            User.is_approved.is_(False),
            _not_deleted(User),
        ).count(),
        "submitted_attempts": Attempt.query.join(User, User.id == Attempt.user_id)
        .join(MockTest, MockTest.id == Attempt.mock_test_id)
        .filter(
            Attempt.status == "submitted",
            _not_deleted(User),
            _not_deleted(MockTest),
        )
        .count(),
        "average_percentage": round(
            Result.query.join(User, User.id == Result.user_id)
            .join(MockTest, MockTest.id == Result.mock_test_id)
            .filter(_not_deleted(User), _not_deleted(MockTest))
            .with_entities(func.avg(Result.percentage))
            .scalar() or 0,
            2,
        ),
    }

    return {
        "approved_users_report": approved_users,
        "user_report": user_report,
        "test_report": test_report,
        "overall_metrics": overall_metrics,
    }


def get_test_report_detail(test_id):
    test = MockTest.query.filter(MockTest.id == test_id, _not_deleted(MockTest)).first()
    if not test:
        raise ValueError("Test report not found.")

    results = (
        Result.query.join(User, User.id == Result.user_id)
        .filter(Result.mock_test_id == test_id, _not_deleted(User))
        .order_by(Result.created_at.desc(), Result.id.desc())
        .all()
    )
    attempt_map = build_result_attempt_map(results)

    rows = [
        {
            "user": result.user,
            "attempt_number": attempt_map[result.id]["attempt_number"],
            "attempt_label": attempt_map[result.id]["attempt_label"],
            "obtained_marks": result.obtained_marks,
            "total_marks": result.total_marks,
            "percentage": result.percentage,
            "submitted_at": result.created_at,
        }
        for result in results
    ]

    return {
        "test": test,
        "rows": rows,
        "summary": {
            "questions": test.total_questions,
            "total_marks": round(test.total_questions * test.marks_per_question, 2),
            "attempts_count": len(rows),
            "users_attended": len({row["user"].id for row in rows}),
            "highest_score": max((row["obtained_marks"] for row in rows), default=0),
        },
    }


def get_user_report_detail(user_id):
    user = User.query.filter(
        User.id == user_id,
        User.role == "user",
        _not_deleted(User),
    ).first()
    if not user:
        raise ValueError("User report not found.")

    results = (
        Result.query.filter_by(user_id=user_id)
        .order_by(Result.created_at.desc(), Result.id.desc())
        .all()
    )
    attempt_map = build_result_attempt_map(results)

    rows = [
        {
            "test": result.mock_test,
            "attempt_number": attempt_map[result.id]["attempt_number"],
            "attempt_label": attempt_map[result.id]["attempt_label"],
            "questions": result.total_questions,
            "total_marks": result.total_marks,
            "obtained_marks": result.obtained_marks,
            "percentage": result.percentage,
            "submitted_at": result.created_at,
        }
        for result in results
    ]

    return {
        "user": user,
        "rows": rows,
        "summary": {
            "tests_attended": len(rows),
            "total_marks": round(sum(row["obtained_marks"] for row in rows), 2),
            "percentage": round(
                sum(row["percentage"] for row in rows) / len(rows),
                2,
            ) if rows else 0,
        },
    }
