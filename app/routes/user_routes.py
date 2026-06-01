from flask import Blueprint

from app.controllers import user_controller
from app.middleware.auth_middleware import approved_user_required


user_bp = Blueprint("user", __name__, url_prefix="/user")


@user_bp.route("/dashboard")
@approved_user_required
def dashboard():
    return user_controller.dashboard()


@user_bp.route("/tests")
@approved_user_required
def tests():
    return user_controller.tests()


@user_bp.route("/results")
@approved_user_required
def results():
    return user_controller.results()


@user_bp.route("/results/<int:result_id>")
@approved_user_required
def result_detail(result_id):
    return user_controller.result_detail(result_id)
