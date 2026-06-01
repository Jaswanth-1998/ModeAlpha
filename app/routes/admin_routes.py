from flask import Blueprint

from app.controllers import admin_controller
from app.middleware.auth_middleware import admin_required


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    return admin_controller.dashboard()


@admin_bp.route("/pending-users")
@admin_required
def pending_users():
    return admin_controller.pending_users()


@admin_bp.route("/tests")
@admin_required
def test_list():
    return admin_controller.test_list()


@admin_bp.route("/tests/create", methods=["GET", "POST"])
@admin_required
def create_test():
    return admin_controller.create_test()


@admin_bp.route("/tests/<int:test_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_test(test_id):
    return admin_controller.edit_test(test_id)


@admin_bp.route("/tests/<int:test_id>/delete", methods=["POST"])
@admin_required
def delete_test(test_id):
    return admin_controller.delete_test(test_id)


@admin_bp.route("/tests/<int:test_id>/upload-questions", methods=["GET", "POST"])
@admin_required
def upload_questions(test_id):
    return admin_controller.upload_questions(test_id)


@admin_bp.route("/reports")
@admin_required
def reports():
    return admin_controller.reports()


@admin_bp.route("/reports/tests/<int:test_id>")
@admin_required
def test_report_detail(test_id):
    return admin_controller.test_report_detail(test_id)


@admin_bp.route("/reports/users/<int:user_id>")
@admin_required
def user_report_detail(user_id):
    return admin_controller.user_report_detail(user_id)


@admin_bp.route("/settings")
@admin_required
def settings():
    return admin_controller.settings()


@admin_bp.route("/settings/users/<int:user_id>/activate", methods=["POST"])
@admin_required
def activate_user(user_id):
    return admin_controller.activate_user(user_id)


@admin_bp.route("/settings/users/<int:user_id>/deactivate", methods=["POST"])
@admin_required
def deactivate_user(user_id):
    return admin_controller.deactivate_user(user_id)


@admin_bp.route("/settings/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    return admin_controller.delete_user(user_id)
