from flask import flash, g, redirect, render_template, request, url_for

from app.services.admin_service import (
    create_mock_test,
    delete_mock_test,
    get_admin_dashboard_data,
    get_mock_test_by_id,
    get_pending_users,
    get_tests_for_admin,
    import_questions_for_test,
    search_users_for_settings,
    set_user_active_state,
    soft_delete_user,
    update_mock_test,
)
from app.services.report_service import (
    get_admin_reports,
    get_test_report_detail,
    get_user_report_detail,
)
from app.utils.pagination import get_page_number, paginate_list


PER_PAGE = 5


def dashboard():
    data = get_admin_dashboard_data()
    query_args = request.args.to_dict(flat=True)
    activities_pagination = paginate_list(
        data["recent_activities"],
        get_page_number(request.args, "activities_page"),
        PER_PAGE,
        endpoint="admin.dashboard",
        page_param="activities_page",
        query_args=query_args,
    )
    data["recent_activities"] = activities_pagination["items"]
    data["recent_activities_pagination"] = activities_pagination
    return render_template("admin/dashboard.html", data=data)


def pending_users():
    users_pagination = paginate_list(
        get_pending_users(),
        get_page_number(request.args),
        PER_PAGE,
        endpoint="admin.pending_users",
        query_args=request.args.to_dict(flat=True),
    )
    return render_template(
        "admin/pending_users.html",
        users=users_pagination["items"],
        users_pagination=users_pagination,
    )


def test_list():
    tests_pagination = paginate_list(
        get_tests_for_admin(),
        get_page_number(request.args),
        PER_PAGE,
        endpoint="admin.test_list",
        query_args=request.args.to_dict(flat=True),
    )
    return render_template(
        "admin/test_list.html",
        tests=tests_pagination["items"],
        tests_pagination=tests_pagination,
    )


def create_test():
    if request.method == "POST":
        try:
            mock_test = create_mock_test(request.form, g.current_user.id)
            flash("Mock test created successfully. Upload questions next.", "success")
            return redirect(url_for("admin.upload_questions", test_id=mock_test.id))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template("admin/test_form.html", test=None)


def edit_test(test_id):
    try:
        test = get_mock_test_by_id(test_id)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("admin.test_list"))

    if request.method == "POST":
        try:
            update_mock_test(test, request.form)
            flash("Mock test updated successfully.", "success")
            return redirect(url_for("admin.test_list"))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template("admin/test_form.html", test=test)


def delete_test(test_id):
    try:
        delete_mock_test(test_id)
        flash("Mock test deleted successfully.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")

    return redirect(url_for("admin.test_list"))


def upload_questions(test_id):
    try:
        test = get_mock_test_by_id(test_id)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("admin.test_list"))

    if request.method == "POST":
        file_storage = request.files.get("question_file")
        try:
            inserted_count = import_questions_for_test(test, file_storage)
            flash(f"{inserted_count} questions imported successfully.", "success")
            return redirect(url_for("admin.test_list"))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template("admin/upload_questions.html", test=test)


def reports():
    report_data = get_admin_reports()
    query_args = request.args.to_dict(flat=True)

    approved_users_pagination = paginate_list(
        report_data["approved_users_report"],
        get_page_number(request.args, "approved_page"),
        PER_PAGE,
        endpoint="admin.reports",
        page_param="approved_page",
        query_args=query_args,
    )
    user_report_pagination = paginate_list(
        report_data["user_report"],
        get_page_number(request.args, "user_report_page"),
        PER_PAGE,
        endpoint="admin.reports",
        page_param="user_report_page",
        query_args=query_args,
    )
    test_report_pagination = paginate_list(
        report_data["test_report"],
        get_page_number(request.args, "test_report_page"),
        PER_PAGE,
        endpoint="admin.reports",
        page_param="test_report_page",
        query_args=query_args,
    )

    report_data["approved_users_report"] = approved_users_pagination["items"]
    report_data["approved_users_pagination"] = approved_users_pagination
    report_data["user_report"] = user_report_pagination["items"]
    report_data["user_report_pagination"] = user_report_pagination
    report_data["test_report"] = test_report_pagination["items"]
    report_data["test_report_pagination"] = test_report_pagination

    return render_template("admin/reports.html", report_data=report_data)


def test_report_detail(test_id):
    try:
        detail_data = get_test_report_detail(test_id)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("admin.reports"))

    detail_pagination = paginate_list(
        detail_data["rows"],
        get_page_number(request.args),
        PER_PAGE,
        endpoint="admin.test_report_detail",
        route_kwargs={"test_id": test_id},
        query_args=request.args.to_dict(flat=True),
    )
    detail_data["rows"] = detail_pagination["items"]
    detail_data["pagination"] = detail_pagination
    return render_template("admin/test_report_detail.html", detail_data=detail_data)


def user_report_detail(user_id):
    try:
        detail_data = get_user_report_detail(user_id)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("admin.reports"))

    detail_pagination = paginate_list(
        detail_data["rows"],
        get_page_number(request.args),
        PER_PAGE,
        endpoint="admin.user_report_detail",
        route_kwargs={"user_id": user_id},
        query_args=request.args.to_dict(flat=True),
    )
    detail_data["rows"] = detail_pagination["items"]
    detail_data["pagination"] = detail_pagination
    return render_template("admin/user_report_detail.html", detail_data=detail_data)


def settings():
    search_term = (request.args.get("search") or "").strip()
    users_pagination = paginate_list(
        search_users_for_settings(search_term),
        get_page_number(request.args),
        PER_PAGE,
        endpoint="admin.settings",
        query_args=request.args.to_dict(flat=True),
    )
    return render_template(
        "admin/settings.html",
        managed_users=users_pagination["items"],
        users_pagination=users_pagination,
        search_term=search_term,
    )


def activate_user(user_id):
    try:
        user = set_user_active_state(user_id, True)
        flash(f"{user.username} is active now.", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return _redirect_to_settings()


def deactivate_user(user_id):
    try:
        user = set_user_active_state(user_id, False)
        flash(f"{user.username} has been deactivated.", "warning")
    except ValueError as exc:
        flash(str(exc), "danger")
    return _redirect_to_settings()


def delete_user(user_id):
    try:
        user = soft_delete_user(user_id)
        flash(f"{user.username} has been marked as deleted.", "warning")
    except ValueError as exc:
        flash(str(exc), "danger")
    return _redirect_to_settings()


def _redirect_to_settings():
    query_args = {}
    search_term = (request.form.get("search") or "").strip()
    page = (request.form.get("page") or "").strip()

    if search_term:
        query_args["search"] = search_term
    if page:
        query_args["page"] = page

    return redirect(url_for("admin.settings", **query_args))
