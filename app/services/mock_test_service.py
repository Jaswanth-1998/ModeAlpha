from datetime import datetime

from app.extensions import db
from app.models.attempt import Attempt
from app.models.mock_test import MockTest
from app.models.question import Question
from app.models.result import Result
from app.utils.helpers import (
    ANSWER_OPTIONS,
    UNANSWERED_TOKEN,
    build_result_attempt_map,
    calculate_elapsed_seconds,
    calculate_remaining_seconds,
    format_attempt_label,
    is_answered_option,
    is_resolved_response,
    is_unanswered_token,
    json_dump,
    json_load,
)


def get_user_tests(user_id):
    tests = (
        MockTest.query.filter(
            MockTest.is_active.is_(True),
            MockTest.total_questions > 0,
            MockTest.delete_flag == "N",
        )
        .order_by(MockTest.created_at.desc())
        .all()
    )

    results = (
        Result.query.filter_by(user_id=user_id)
        .order_by(Result.created_at.asc(), Result.id.asc())
        .all()
    )
    result_attempt_map = build_result_attempt_map(results)

    latest_result_map = {}
    completed_attempt_count_map = {}
    for result in results:
        latest_result_map[result.mock_test_id] = result
        completed_attempt_count_map[result.mock_test_id] = (
            completed_attempt_count_map.get(result.mock_test_id, 0) + 1
        )

    attempts = (
        Attempt.query.filter_by(user_id=user_id)
        .order_by(Attempt.started_at.desc(), Attempt.id.desc())
        .all()
    )
    active_attempt_map = {}
    for attempt in attempts:
        if attempt.status not in {"in_progress", "paused"}:
            continue
        active_attempt_map.setdefault(attempt.mock_test_id, attempt)

    test_rows = []
    for test in tests:
        latest_result = latest_result_map.get(test.id)
        latest_attempt_meta = (
            result_attempt_map.get(latest_result.id, {})
            if latest_result
            else {}
        )
        active_attempt = active_attempt_map.get(test.id)

        test_rows.append(
            {
                "test": test,
                "latest_result": latest_result,
                "completed_attempts_count": completed_attempt_count_map.get(test.id, 0),
                "latest_attempt_label": latest_attempt_meta.get("attempt_label"),
                "active_attempt": active_attempt,
                "remaining_seconds": (
                    _get_attempt_remaining_seconds(active_attempt)
                    if active_attempt
                    else None
                ),
            }
        )

    return test_rows


def create_or_resume_attempt(user_id, test_id):
    test = db.session.get(MockTest, test_id)
    if not test or test.delete_flag == "Y" or not test.is_active:
        raise ValueError("The selected test is not available.")
    if test.total_questions == 0:
        raise ValueError("This test does not have questions yet.")

    active_attempt = (
        Attempt.query.filter_by(
            user_id=user_id,
            mock_test_id=test_id,
        )
        .filter(Attempt.status.in_(["in_progress", "paused"]))
        .order_by(Attempt.started_at.desc(), Attempt.id.desc())
        .first()
    )
    if active_attempt:
        if active_attempt.status == "paused":
            _resume_attempt(active_attempt)
        return active_attempt, "resumed", _get_resume_question_number(active_attempt)

    prior_attempts_count = (
        Attempt.query.filter_by(
            user_id=user_id,
            mock_test_id=test_id,
            status="submitted",
        ).count()
    )

    attempt = Attempt(user_id=user_id, mock_test_id=test_id)
    db.session.add(attempt)
    db.session.commit()

    attempt_mode = "retest" if prior_attempts_count else "created"
    return attempt, attempt_mode, 1


def get_attempt_question_context(attempt_id, user_id, question_number):
    attempt = _get_attempt(attempt_id, user_id)
    if attempt.status == "submitted" and attempt.result:
        raise ValueError("This attempt has already been submitted.")
    if attempt.status == "paused":
        raise ValueError("This attempt is paused. Resume the test to continue.")

    remaining_seconds = calculate_remaining_seconds(
        attempt.mock_test.time_limit_minutes,
        elapsed_seconds=attempt.elapsed_seconds,
        last_resumed_at=attempt.last_resumed_at,
        status=attempt.status,
    )
    if remaining_seconds <= 0:
        raise TimeoutError("Attempt expired.")

    questions = attempt.mock_test.questions
    if not questions:
        raise ValueError("This test does not contain questions.")

    total_questions = len(questions)
    if question_number < 1 or question_number > total_questions:
        raise ValueError("Question number is out of range.")

    question = questions[question_number - 1]
    visited_question_ids = _mark_question_visited(attempt, question.id)
    answers = json_load(attempt.answers_json)
    current_value = answers.get(str(question.id))
    answered_question_ids = _get_answered_question_ids(answers)
    resolved_question_ids = _get_resolved_question_ids(answers)
    unresolved_question_numbers = [
        item.question_order
        for item in questions
        if item.id not in resolved_question_ids
    ]

    return {
        "attempt": attempt,
        "mock_test": attempt.mock_test,
        "question": question,
        "question_number": question_number,
        "total_questions": total_questions,
        "selected_option": current_value if is_answered_option(current_value) else None,
        "is_marked_unanswered": is_unanswered_token(current_value),
        "question_resolution_state": _get_question_resolution_state(current_value),
        "answered_count": len(answered_question_ids),
        "resolved_count": len(resolved_question_ids),
        "remaining_seconds": remaining_seconds,
        "answered_question_ids": answered_question_ids,
        "resolved_question_ids": resolved_question_ids,
        "visited_question_ids": visited_question_ids,
        "show_final_submit": len(resolved_question_ids) == total_questions,
        "unresolved_question_numbers": unresolved_question_numbers,
    }


def save_answer_for_attempt(attempt_id, user_id, question_id, selected_option):
    attempt = _get_attempt(attempt_id, user_id)
    if attempt.status == "submitted":
        raise ValueError("This attempt has already been submitted.")
    if attempt.status == "paused":
        raise ValueError("This attempt is paused. Resume the test to continue.")

    remaining_seconds = calculate_remaining_seconds(
        attempt.mock_test.time_limit_minutes,
        elapsed_seconds=attempt.elapsed_seconds,
        last_resumed_at=attempt.last_resumed_at,
        status=attempt.status,
    )
    if remaining_seconds <= 0:
        raise ValueError("Time is up for this attempt.")

    question = db.session.get(Question, question_id)
    if not question or question.mock_test_id != attempt.mock_test_id:
        raise ValueError("Question not found for this test.")

    answers = json_load(attempt.answers_json)
    answer_key = str(question.id)
    existing_value = answers.get(answer_key)
    cleaned_option = (selected_option or "").strip().upper()

    if cleaned_option == UNANSWERED_TOKEN:
        answers[answer_key] = UNANSWERED_TOKEN
    elif cleaned_option:
        if cleaned_option not in ANSWER_OPTIONS:
            raise ValueError("Invalid answer option.")
        answers[answer_key] = cleaned_option
    elif is_unanswered_token(existing_value):
        answers[answer_key] = UNANSWERED_TOKEN
    else:
        answers.pop(answer_key, None)

    attempt.answers_json = json_dump(answers)
    db.session.commit()

    current_value = answers.get(answer_key)
    answered_question_ids = _get_answered_question_ids(answers)
    resolved_question_ids = _get_resolved_question_ids(answers)

    return {
        "selected_option": current_value if is_answered_option(current_value) else None,
        "is_marked_unanswered": is_unanswered_token(current_value),
        "resolution_state": _get_question_resolution_state(current_value),
        "answered_count": len(answered_question_ids),
        "resolved_count": len(resolved_question_ids),
        "show_final_submit": len(resolved_question_ids) == len(attempt.mock_test.questions),
    }


def pause_attempt_for_user(attempt_id, user_id):
    attempt = _get_attempt(attempt_id, user_id)
    if attempt.status == "submitted":
        raise ValueError("This attempt has already been submitted.")
    if attempt.status == "paused":
        return attempt

    remaining_seconds = _get_attempt_remaining_seconds(attempt)
    if remaining_seconds <= 0:
        raise TimeoutError("Attempt expired.")

    now = datetime.utcnow()
    attempt.elapsed_seconds = calculate_elapsed_seconds(
        attempt.elapsed_seconds,
        attempt.last_resumed_at,
        attempt.status,
    )
    attempt.paused_at = now
    attempt.last_resumed_at = now
    attempt.status = "paused"
    db.session.commit()
    return attempt


def submit_attempt_for_user(attempt_id, user_id, allow_incomplete=False):
    attempt = _get_attempt(attempt_id, user_id)
    if attempt.result:
        return attempt.result
    if attempt.status == "submitted":
        raise ValueError("This attempt has already been submitted.")

    answers = json_load(attempt.answers_json)
    questions = attempt.mock_test.questions
    resolved_question_ids = _get_resolved_question_ids(answers)

    if not allow_incomplete and len(resolved_question_ids) < len(questions):
        raise ValueError(
            "Answer or mark all questions as unanswered before final submit."
        )

    correct = 0
    wrong = 0
    unanswered = 0

    for question in questions:
        selected_option = answers.get(str(question.id))
        if not is_answered_option(selected_option):
            unanswered += 1
            continue
        if selected_option == question.correct_answer:
            correct += 1
        else:
            wrong += 1

    mock_test = attempt.mock_test
    total_questions = len(questions)
    total_marks = total_questions * mock_test.marks_per_question
    obtained_marks = correct * mock_test.marks_per_question

    if mock_test.negative_marking_enabled:
        obtained_marks -= wrong * mock_test.negative_mark_value
    if mock_test.unanswered_negative_marking_enabled:
        obtained_marks -= unanswered * mock_test.unanswered_negative_mark_value

    percentage = (obtained_marks / total_marks * 100) if total_marks else 0
    time_taken_seconds = calculate_elapsed_seconds(
        attempt.elapsed_seconds,
        attempt.last_resumed_at,
        attempt.status,
    )

    attempt.status = "submitted"
    attempt.submitted_at = datetime.utcnow()
    attempt.paused_at = None
    attempt.elapsed_seconds = time_taken_seconds
    attempt.last_resumed_at = attempt.submitted_at
    attempt.time_taken_seconds = time_taken_seconds

    result = Result(
        attempt=attempt,
        user_id=user_id,
        mock_test_id=mock_test.id,
        total_questions=total_questions,
        correct_answers=correct,
        wrong_answers=wrong,
        unanswered_answers=unanswered,
        obtained_marks=round(obtained_marks, 2),
        total_marks=round(total_marks, 2),
        percentage=round(percentage, 2),
    )
    db.session.add(result)
    db.session.commit()
    return result


def get_user_results(user_id):
    results = (
        Result.query.filter_by(user_id=user_id)
        .join(MockTest, MockTest.id == Result.mock_test_id)
        .order_by(Result.created_at.desc(), Result.id.desc())
        .all()
    )
    result_attempt_map = build_result_attempt_map(results)

    return [
        {
            "result": result,
            "attempt_number": result_attempt_map[result.id]["attempt_number"],
            "attempt_label": result_attempt_map[result.id]["attempt_label"],
        }
        for result in results
    ]


def get_result_detail_for_user(result_id, user_id):
    result = Result.query.filter_by(id=result_id, user_id=user_id).first()
    if not result:
        raise ValueError("Result not found.")

    related_results = (
        Result.query.filter_by(user_id=user_id, mock_test_id=result.mock_test_id)
        .order_by(Result.created_at.asc(), Result.id.asc())
        .all()
    )
    result_attempt_map = build_result_attempt_map(related_results)
    current_attempt_meta = result_attempt_map.get(
        result.id,
        {
            "attempt_number": 1,
            "attempt_label": format_attempt_label(1),
        },
    )

    answers = json_load(result.attempt.answers_json)
    question_rows = []
    for question in result.mock_test.questions:
        selected_value = answers.get(str(question.id))
        question_rows.append(
            {
                "question_order": question.question_order,
                "question_text": question.question_text,
                "selected_option": (
                    selected_value
                    if is_answered_option(selected_value)
                    else "Left Unanswered"
                ),
                "correct_answer": question.correct_answer,
            }
        )

    return {
        "result": result,
        "attempt_number": current_attempt_meta["attempt_number"],
        "attempt_label": current_attempt_meta["attempt_label"],
        "question_rows": question_rows,
    }


def _get_attempt(attempt_id, user_id):
    attempt = Attempt.query.filter_by(id=attempt_id, user_id=user_id).first()
    if not attempt:
        raise ValueError("Attempt not found.")
    return attempt


def _get_resume_question_number(attempt):
    answers = json_load(attempt.answers_json)
    resolved_question_ids = _get_resolved_question_ids(answers)
    for question in attempt.mock_test.questions:
        if question.id not in resolved_question_ids:
            return question.question_order

    return len(attempt.mock_test.questions) or 1


def _get_attempt_remaining_seconds(attempt):
    return calculate_remaining_seconds(
        attempt.mock_test.time_limit_minutes,
        elapsed_seconds=attempt.elapsed_seconds,
        last_resumed_at=attempt.last_resumed_at,
        status=attempt.status,
    )


def _resume_attempt(attempt):
    attempt.status = "in_progress"
    attempt.paused_at = None
    attempt.last_resumed_at = datetime.utcnow()
    db.session.commit()
    return attempt


def _mark_question_visited(attempt, question_id):
    visited_question_ids = _load_visited_question_ids(attempt)
    if question_id not in visited_question_ids:
        visited_question_ids.add(question_id)
        attempt.visited_questions_json = json_dump(sorted(visited_question_ids))
        db.session.commit()
    return visited_question_ids


def _load_visited_question_ids(attempt):
    raw_value = attempt.visited_questions_json or "[]"
    try:
        loaded_value = json_load(raw_value)
        if isinstance(loaded_value, list):
            return {int(value) for value in loaded_value}
    except (TypeError, ValueError):
        pass
    return set()


def _get_answered_question_ids(answers):
    return {
        int(question_id)
        for question_id, selected_option in answers.items()
        if is_answered_option(selected_option)
    }


def _get_resolved_question_ids(answers):
    return {
        int(question_id)
        for question_id, selected_option in answers.items()
        if is_resolved_response(selected_option)
    }


def _get_question_resolution_state(value):
    if is_answered_option(value):
        return "answered"
    if is_unanswered_token(value):
        return "resolved-unanswered"
    return "unresolved"
