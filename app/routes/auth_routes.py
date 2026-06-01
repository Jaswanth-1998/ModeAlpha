from flask import Blueprint

from app.controllers import auth_controller
from app.middleware.auth_middleware import login_required


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    return auth_controller.register()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    return auth_controller.login()


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return auth_controller.profile()


@auth_bp.route("/logout")
@login_required
def logout():
    return auth_controller.logout()
