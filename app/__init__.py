from flask import Flask, g

from app.commands import register_commands
from app.config.settings import config_by_name
from app.extensions import db, migrate
from app.middleware.auth_middleware import load_logged_in_user
from app.routes.admin_routes import admin_bp
from app.routes.api_routes import api_bp
from app.routes.auth_routes import auth_bp
from app.routes.main_routes import main_bp
from app.routes.test_routes import test_bp
from app.routes.user_routes import user_bp
def create_app(config_name="development"):
    app = Flask(
        __name__,
        instance_relative_config=True,
        instance_path=str(config_by_name[config_name].INSTANCE_DIR),
    )
    app.config.from_object(config_by_name[config_name])
    config_by_name[config_name].ensure_directories()

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True, compare_type=True)

    from app import models  # noqa: F401

    register_commands(app)

    app.before_request(load_logged_in_user)

    @app.context_processor
    def inject_current_user():
        return {"current_user": getattr(g, "current_user", None)}

    @app.after_request
    def disable_cache_for_authenticated_pages(response):
        if getattr(g, "current_user", None):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(test_bp)
    app.register_blueprint(api_bp)

    return app
