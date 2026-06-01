from functools import wraps
from time import time

from flask import current_app, flash, g, jsonify, redirect, request, session, url_for

from app.extensions import db
from app.models.user import User


def load_logged_in_user():
    user_id = session.get("user_id")
    g.current_user = None
    g.session_expired = False
    g.account_access_removed = False

    if user_id and _session_has_expired():
        session.clear()
        g.session_expired = True
        return

    if not user_id:
        return

    session["last_activity_at"] = time()
    g.current_user = db.session.get(User, user_id)

    if (
        not g.current_user
        or g.current_user.delete_flag == "Y"
        or not g.current_user.is_active
    ):
        g.account_access_removed = True
        g.current_user = None
        session.clear()


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not g.current_user:
            return _unauthorized_response("Please log in to continue.")
        return view_func(*args, **kwargs)

    return wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not g.current_user:
            return _unauthorized_response("Please log in to continue.")
        if g.current_user.role != "admin":
            return _forbidden_response("Admin access is required.")
        return view_func(*args, **kwargs)

    return wrapped_view


def approved_user_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not g.current_user:
            return _unauthorized_response("Please log in to continue.")
        if g.current_user.role != "user":
            return _forbidden_response("User access is required.")
        if not g.current_user.is_approved:
            return _forbidden_response("Your account is waiting for admin approval.")
        return view_func(*args, **kwargs)

    return wrapped_view


def _unauthorized_response(message):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "message": message}), 401

    if getattr(g, "session_expired", False):
        flash("Your session expired. Please log in again.", "warning")
    elif getattr(g, "account_access_removed", False):
        flash("Your account is no longer active. Please contact the admin.", "warning")

    return redirect(url_for("auth.login"))


def _forbidden_response(message):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "message": message}), 403
    if g.current_user and g.current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("user.dashboard"))


def _session_has_expired():
    last_activity_at = session.get("last_activity_at")
    if not last_activity_at:
        return True

    timeout_seconds = current_app.config["PERMANENT_SESSION_LIFETIME"].total_seconds()
    return (time() - float(last_activity_at)) > timeout_seconds
