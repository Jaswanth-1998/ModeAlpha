from flask import Blueprint

from app.controllers import main_controller


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return main_controller.index()
