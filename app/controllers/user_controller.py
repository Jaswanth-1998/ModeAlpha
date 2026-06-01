from flask import flash, g, redirect, render_template, request, url_for

from app.services.mock_test_service import get_result_detail_for_user, get_user_results, get_user_tests
from app.services.report_service import get_user_dashboard_data
from app.utils.pagination import get_page_number, paginate_list


PER_PAGE = 5


def dashboard():
    data = get_user_dashboard_data(g.current_user.id)
    recent_results_pagination = paginate_list(
        data["recent_results"],
        get_page_number(request.args, "recent_results_page"),
        PER_PAGE,
        endpoint="user.dashboard",
        page_param="recent_results_page",
        query_args=request.args.to_dict(flat=True),
    )
    data["recent_results"] = recent_results_pagination["items"]
    data["recent_results_pagination"] = recent_results_pagination
    return render_template("user/dashboard.html", data=data)


def tests():
    tests_data = get_user_tests(g.current_user.id)
    return render_template("user/test_list.html", tests_data=tests_data)


def results():
    results_pagination = paginate_list(
        get_user_results(g.current_user.id),
        get_page_number(request.args),
        PER_PAGE,
        endpoint="user.results",
        query_args=request.args.to_dict(flat=True),
    )
    return render_template(
        "user/results.html",
        results_data=results_pagination["items"],
        results_pagination=results_pagination,
    )


def result_detail(result_id):
    try:
        result_data = get_result_detail_for_user(result_id, g.current_user.id)
        question_rows_pagination = paginate_list(
            result_data["question_rows"],
            get_page_number(request.args),
            PER_PAGE,
            endpoint="user.result_detail",
            query_args=request.args.to_dict(flat=True),
            route_kwargs={"result_id": result_id},
        )
        result_data["question_rows"] = question_rows_pagination["items"]
        result_data["question_rows_pagination"] = question_rows_pagination
        return render_template("user/result_detail.html", result_data=result_data)
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("user.results"))
