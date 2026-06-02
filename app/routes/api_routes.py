from flask import Blueprint

from app.controllers import api_controller
from app.middleware.auth_middleware import admin_required, approved_user_required


api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/admin/users/<int:user_id>/approve", methods=["POST"])
@admin_required
def approve_user_api(user_id):
    return api_controller.approve_user(user_id)


@api_bp.route("/admin/users/<int:user_id>/reject", methods=["POST"])
@admin_required
def reject_user_api(user_id):
    return api_controller.reject_user(user_id)


@api_bp.route("/admin/dashboard-analytics")
@admin_required
def admin_dashboard_analytics():
    return api_controller.admin_dashboard_analytics()


@api_bp.route("/user/dashboard-metrics")
@approved_user_required
def user_dashboard_metrics():
    return api_controller.user_dashboard_metrics()


@api_bp.route("/tests/attempts/<int:attempt_id>/answers", methods=["POST"])
@approved_user_required
def save_answer(attempt_id):
    return api_controller.save_answer(attempt_id)


@api_bp.route("/tests/attempts/<int:attempt_id>/submit", methods=["POST"])
@approved_user_required
def submit_attempt_api(attempt_id):
    return api_controller.submit_attempt(attempt_id)
