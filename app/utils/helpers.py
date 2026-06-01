import json
import re
from datetime import datetime


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


def calculate_elapsed_seconds(elapsed_seconds, last_resumed_at, status):
    elapsed = int(elapsed_seconds or 0)
    if status == "in_progress" and last_resumed_at:
        elapsed += int((datetime.utcnow() - last_resumed_at).total_seconds())
    return max(elapsed, 0)


def calculate_remaining_seconds(time_limit_minutes, elapsed_seconds=0, last_resumed_at=None, status="in_progress"):
    elapsed = calculate_elapsed_seconds(elapsed_seconds, last_resumed_at, status)
    total_seconds = time_limit_minutes * 60
    return max(total_seconds - elapsed, 0)
