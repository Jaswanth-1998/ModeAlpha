import json
import re
from datetime import datetime


UNANSWERED_TOKEN = "__UNANSWERED__"
ANSWER_OPTIONS = {"A", "B", "C", "D"}


def normalize_email(value):
    return (value or "").strip().lower()


def normalize_mobile(value):
    mobile = re.sub(r"\D", "", value or "")
    if len(mobile) < 10:
        raise ValueError("Please enter a valid mobile number.")
    return mobile


def parse_bool(value):
    return str(value).lower() in {"1", "true", "yes", "on"}


def parse_int(value, field_name):
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid integer.") from exc


def parse_float(value, field_name):
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid number.") from exc


def json_load(value):
    try:
        return json.loads(value or "{}")
    except json.JSONDecodeError:
        return {}


def json_dump(value):
    return json.dumps(value)


def is_answered_option(value):
    return str(value or "").upper() in ANSWER_OPTIONS


def is_unanswered_token(value):
    return str(value or "").upper() == UNANSWERED_TOKEN


def is_resolved_response(value):
    return is_answered_option(value) or is_unanswered_token(value)


def format_attempt_label(attempt_number):
    attempt_number = int(attempt_number or 0)
    if attempt_number <= 0:
        return "Attempt"

    if 10 <= (attempt_number % 100) <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(attempt_number % 10, "th")

    return f"{attempt_number}{suffix} Attempt"


def build_result_attempt_map(results):
    grouped_counts = {}
    attempt_map = {}

    ordered_results = sorted(
        results,
        key=lambda result: (
            result.user_id,
            result.mock_test_id,
            result.created_at,
            result.id,
        ),
    )

    for result in ordered_results:
        group_key = (result.user_id, result.mock_test_id)
        grouped_counts[group_key] = grouped_counts.get(group_key, 0) + 1
        attempt_number = grouped_counts[group_key]
        attempt_map[result.id] = {
            "attempt_number": attempt_number,
            "attempt_label": format_attempt_label(attempt_number),
        }

    return attempt_map


def calculate_elapsed_seconds(elapsed_seconds, last_resumed_at, status):
    elapsed = int(elapsed_seconds or 0)
    if status == "in_progress" and last_resumed_at:
        elapsed += int((datetime.utcnow() - last_resumed_at).total_seconds())
    return max(elapsed, 0)


def calculate_remaining_seconds(time_limit_minutes, elapsed_seconds=0, last_resumed_at=None, status="in_progress"):
    elapsed = calculate_elapsed_seconds(elapsed_seconds, last_resumed_at, status)
    total_seconds = time_limit_minutes * 60
    return max(total_seconds - elapsed, 0)
