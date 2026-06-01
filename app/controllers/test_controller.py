from flask import flash, g, redirect, render_template, url_for

from app.services.mock_test_service import (
    create_or_resume_attempt,
    get_attempt_question_context,
    pause_attempt_for_user,
    submit_attempt_for_user,
)


def start_test(test_id):
    try:
        attempt, created, question_number = create_or_resume_attempt(g.current_user.id, test_id)
        message = "Test started successfully." if created else "Resuming your existing attempt."
        flash(message, "success")
        return redirect(
            url_for(
                "tests.question_page",
                attempt_id=attempt.id,
                question_number=question_number,
            )
        )
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("user.tests"))


def question_page(attempt_id, question_number):
    try:
        context = get_attempt_question_context(attempt_id, g.current_user.id, question_number)
        return render_template("mock_tests/question.html", **context)
    except TimeoutError:
        result = submit_attempt_for_user(attempt_id, g.current_user.id)
        flash("Time is up. Your test has been submitted automatically.", "warning")
        return redirect(url_for("user.result_detail", result_id=result.id))
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("user.tests"))


def submit_test(attempt_id):
    try:
        result = submit_attempt_for_user(attempt_id, g.current_user.id)
        flash("Test submitted successfully.", "success")
        return redirect(url_for("user.result_detail", result_id=result.id))
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("user.tests"))


def pause_test(attempt_id):
    try:
        pause_attempt_for_user(attempt_id, g.current_user.id)
        flash("Test paused. Resume whenever you are ready.", "info")
        return redirect(url_for("user.tests"))
    except TimeoutError:
        result = submit_attempt_for_user(attempt_id, g.current_user.id)
        flash("Time is up. Your test has been submitted automatically.", "warning")
        return redirect(url_for("user.result_detail", result_id=result.id))
    except ValueError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("user.tests"))
