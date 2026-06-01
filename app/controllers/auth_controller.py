from flask import flash, g, redirect, render_template, request, url_for

from app.services.auth_service import (
    authenticate_user,
    login_user_session,
    logout_user_session,
    register_user,
    update_profile,
)


def register():
    if request.method == "POST":
        try:
            register_user(request.form)
            flash("Registration successful. Please wait for admin approval.", "success")
            return redirect(url_for("auth.login"))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template("auth/register.html")


def login():
    if request.method == "POST":
        try:
            user = authenticate_user(
                login_identifier=request.form.get("login_identifier", ""),
                password=request.form.get("password", ""),
            )
            login_user_session(user)
            flash("Login successful.", "success")

            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))

            return redirect(url_for("user.dashboard"))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template("auth/login.html")


def profile():
    if request.method == "POST":
        try:
            update_profile(g.current_user, request.form)
            login_user_session(g.current_user)
            flash("Profile updated successfully.", "success")
            return redirect(url_for("auth.profile"))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template("auth/profile.html")


def logout():
    logout_user_session()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
