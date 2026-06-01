from flask import g, jsonify, request, url_for

from app.services.admin_service import approve_user_account, get_admin_dashboard_data
from app.services.mock_test_service import (
    save_answer_for_attempt,
    submit_attempt_for_user,
)
from app.services.report_service import get_user_dashboard_data


def approve_user(user_id):
    try:
        user = approve_user_account(user_id)
        return jsonify(
            {
                "success": True,
                "message": f"{user.username} approved successfully.",
                "user_id": user.id,
            }
        )
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

def admin_dashboard_analytics():
    data = get_admin_dashboard_data()
    return jsonify(
        {
            "success": True,
            "metrics": {
                "total_users": data["total_users"],
                "total_tests": data["total_tests"],
                "users_attended": data["users_attended"],
                "pending_approvals": data["pending_approvals"],
            },
        }
    )

def user_dashboard_metrics():
    data = get_user_dashboard_data(g.current_user.id)
    return jsonify(
        {
            "success": True,
            "metrics": {
                "available_tests": data["total_available_tests"],
                "attended_tests": data["attended_tests"],
                "average_marks": data["average_marks"],
            },
        }
    )

def save_answer(attempt_id):
    payload = request.get_json(silent=True) or {}
    try:
        saved_answer = save_answer_for_attempt(
            attempt_id=attempt_id,
            user_id=g.current_user.id,
            question_id=payload.get("question_id"),
            selected_option=payload.get("selected_option"),
        )
        return jsonify(
            {
                "success": True,
                "message": "Answer saved.",
                "selected_option": saved_answer,
            }
        )
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

def submit_attempt(attempt_id):
    try:
        result = submit_attempt_for_user(attempt_id, g.current_user.id)
        return jsonify(
            {
                "success": True,
                "message": "Test submitted successfully.",
                "redirect_url": url_for("user.result_detail", result_id=result.id),
            }
        )
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
