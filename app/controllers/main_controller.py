from flask import g, redirect, render_template, url_for


def index():
    if not g.current_user:
        return render_template("home.html")

    if g.current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))

    return redirect(url_for("user.dashboard"))
