from flask import Blueprint

from app.controllers import test_controller
from app.middleware.auth_middleware import approved_user_required


test_bp = Blueprint("tests", __name__, url_prefix="/tests")


@test_bp.route("/<int:test_id>/start", methods=["POST"])
@approved_user_required
def start_test(test_id):
    return test_controller.start_test(test_id)


@test_bp.route("/attempts/<int:attempt_id>/questions/<int:question_number>")
@approved_user_required
def question_page(attempt_id, question_number):
    return test_controller.question_page(attempt_id, question_number)


@test_bp.route("/attempts/<int:attempt_id>/submit", methods=["POST"])
@approved_user_required
def submit_test(attempt_id):
    return test_controller.submit_test(attempt_id)


@test_bp.route("/attempts/<int:attempt_id>/pause", methods=["POST"])
@approved_user_required
def pause_test(attempt_id):
    return test_controller.pause_test(attempt_id)
