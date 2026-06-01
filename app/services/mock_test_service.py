from datetime import datetime

from app.extensions import db
from app.models.attempt import Attempt
from app.models.mock_test import MockTest
from app.models.question import Question
from app.models.result import Result
from app.utils.helpers import (
    calculate_elapsed_seconds,
    calculate_remaining_seconds,
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
    results = Result.query.filter_by(user_id=user_id).all()
    result_map = {result.mock_test_id: result for result in results}
    attempts = (
        Attempt.query.filter_by(user_id=user_id)
        .order_by(Attempt.started_at.desc())
        .all()
    )
    active_attempt_map = {}
    for attempt in attempts:
        if attempt.status not in {"in_progress", "paused"}:
            continue
        active_attempt_map.setdefault(attempt.mock_test_id, attempt)

    return [
        {
            "test": test,
            "result": result_map.get(test.id),
            "active_attempt": active_attempt_map.get(test.id),
            "remaining_seconds": (
                _get_attempt_remaining_seconds(active_attempt_map[test.id])
                if test.id in active_attempt_map
                else None
            ),
        }
        for test in tests
    ]


def create_or_resume_attempt(user_id, test_id):
    test = db.session.get(MockTest, test_id)
    if not test or test.delete_flag == "Y" or not test.is_active:
        raise ValueError("The selected test is not available.")
    if test.total_questions == 0:
        raise ValueError("This test does not have questions yet.")

    existing_result = Result.query.filter_by(user_id=user_id, mock_test_id=test_id).first()
    if existing_result:
        raise ValueError("You have already submitted this test.")

    active_attempt = Attempt.query.filter_by(
        user_id=user_id,
        mock_test_id=test_id,
    ).filter(Attempt.status.in_(["in_progress", "paused"])).order_by(Attempt.started_at.desc()).first()
    if active_attempt:
        if active_attempt.status == "paused":
            _resume_attempt(active_attempt)
        return active_attempt, False, _get_resume_question_number(active_attempt)

    attempt = Attempt(user_id=user_id, mock_test_id=test_id)
    db.session.add(attempt)
    db.session.commit()
    return attempt, True, 1


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
    selected_option = answers.get(str(question.id))
    answered_question_ids = {int(question_id) for question_id in answers.keys()}

    return {
        "attempt": attempt,
        "mock_test": attempt.mock_test,
        "question": question,
        "question_number": question_number,
        "total_questions": total_questions,
        "selected_option": selected_option,
        "answered_count": len(answered_question_ids),
        "remaining_seconds": remaining_seconds,
        "answered_question_ids": answered_question_ids,
        "visited_question_ids": visited_question_ids,
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
    cleaned_option = (selected_option or "").strip().upper()

    if cleaned_option:
        if cleaned_option not in {"A", "B", "C", "D"}:
            raise ValueError("Invalid answer option.")
        answers[str(question.id)] = cleaned_option
    else:
        answers.pop(str(question.id), None)

    attempt.answers_json = json_dump(answers)
    db.session.commit()
    return answers.get(str(question.id))


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


def submit_attempt_for_user(attempt_id, user_id):
    attempt = _get_attempt(attempt_id, user_id)
    if attempt.result:
        return attempt.result
    if attempt.status == "submitted":
        raise ValueError("This attempt has already been submitted.")

    answers = json_load(attempt.answers_json)
    questions = attempt.mock_test.questions

    correct = 0
    wrong = 0
    unanswered = 0

    for question in questions:
        selected_option = answers.get(str(question.id))
        if not selected_option:
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
        .order_by(Result.created_at.desc())
        .all()
    )
    return results


def get_result_detail_for_user(result_id, user_id):
    result = Result.query.filter_by(id=result_id, user_id=user_id).first()
    if not result:
        raise ValueError("Result not found.")

    answers = json_load(result.attempt.answers_json)
    question_rows = []
    for question in result.mock_test.questions:
        question_rows.append(
            {
                "question_order": question.question_order,
                "question_text": question.question_text,
                "selected_option": answers.get(str(question.id), "-"),
                "correct_answer": question.correct_answer,
            }
        )

    return {
        "result": result,
        "question_rows": question_rows,
    }


def _get_attempt(attempt_id, user_id):
    attempt = Attempt.query.filter_by(id=attempt_id, user_id=user_id).first()
    if not attempt:
        raise ValueError("Attempt not found.")
    return attempt


def _get_resume_question_number(attempt):
    answers = json_load(attempt.answers_json)
    for question in attempt.mock_test.questions:
        if str(question.id) not in answers:
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
