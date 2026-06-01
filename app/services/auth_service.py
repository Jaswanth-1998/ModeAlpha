from datetime import datetime
from time import time

from sqlalchemy import or_
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.user import User
from app.utils.helpers import normalize_email, normalize_mobile


ACTIVE_DELETE_FLAG = "N"
DELETED_DELETE_FLAG = "Y"


def register_user(form_data):
    username = (form_data.get("username") or "").strip()
    email = normalize_email(form_data.get("email"))
    mobile_number = normalize_mobile(form_data.get("mobile_number"))
    password = (form_data.get("password") or "").strip()
    date_of_birth_raw = (form_data.get("date_of_birth") or "").strip()

    if not all([username, email, mobile_number, password, date_of_birth_raw]):
        raise ValueError("All registration fields are required.")

    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    _raise_if_user_conflicts(
        username=username,
        email=email,
        mobile_number=mobile_number,
    )

    try:
        date_of_birth = datetime.strptime(date_of_birth_raw, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("Please provide a valid date of birth.") from exc

    user = User(
        username=username,
        email=email,
        mobile_number=mobile_number,
        date_of_birth=date_of_birth,
        password_hash=generate_password_hash(password),
        role="user",
        is_approved=False,
        is_active=True,
        delete_flag=ACTIVE_DELETE_FLAG,
    )
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(login_identifier, password):
    identifier = (login_identifier or "").strip()
    if not identifier or not password:
        raise ValueError("Username/email and password are required.")

    user = (
        User.query.filter(User.delete_flag != DELETED_DELETE_FLAG)
        .filter(
            (User.username == identifier)
            | (User.email == normalize_email(identifier))
        )
        .first()
    )

    if not user or not check_password_hash(user.password_hash, password):
        raise ValueError("Invalid login credentials.")

    if user.delete_flag == DELETED_DELETE_FLAG:
        raise ValueError("This account has been deleted. Please contact the admin.")

    if not user.is_active:
        raise ValueError("This account is deactivated. Please contact the admin.")

    if user.role == "user" and not user.is_approved:
        raise ValueError("Your account is pending admin approval.")

    return user


def login_user_session(user):
    session.clear()
    session["user_id"] = user.id
    session["role"] = user.role
    session["last_activity_at"] = time()


def logout_user_session():
    session.clear()


def update_profile(user, form_data):
    username = (form_data.get("username") or "").strip()
    email = normalize_email(form_data.get("email"))
    mobile_number = normalize_mobile(form_data.get("mobile_number"))
    date_of_birth_raw = (form_data.get("date_of_birth") or "").strip()
    current_password = (form_data.get("current_password") or "").strip()
    new_password = (form_data.get("new_password") or "").strip()
    confirm_password = (form_data.get("confirm_password") or "").strip()

    if not all([username, email, mobile_number, date_of_birth_raw]):
        raise ValueError("All profile fields are required.")

    _raise_if_user_conflicts(
        username=username,
        email=email,
        mobile_number=mobile_number,
        exclude_user_id=user.id,
        duplicate_context="profile",
    )

    try:
        user.date_of_birth = datetime.strptime(date_of_birth_raw, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("Please provide a valid date of birth.") from exc

    user.username = username
    user.email = email
    user.mobile_number = mobile_number

    if current_password or new_password or confirm_password:
        if not all([current_password, new_password, confirm_password]):
            raise ValueError("Fill in current password, new password, and confirm password to change it.")
        if not check_password_hash(user.password_hash, current_password):
            raise ValueError("Current password is incorrect.")
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters long.")
        if new_password != confirm_password:
            raise ValueError("New password and confirm password do not match.")

        user.password_hash = generate_password_hash(new_password)

    db.session.commit()
    return user


def _raise_if_user_conflicts(
    username=None,
    email=None,
    mobile_number=None,
    exclude_user_id=None,
    duplicate_context="registration",
):
    filters = []
    if username:
        filters.append(User.username == username)
    if email:
        filters.append(User.email == email)
    if mobile_number:
        filters.append(User.mobile_number == mobile_number)

    if not filters:
        return

    query = User.query.filter(User.delete_flag != DELETED_DELETE_FLAG).filter(or_(*filters))
    if exclude_user_id is not None:
        query = query.filter(User.id != exclude_user_id)

    for existing_user in query.all():
        if email and existing_user.email == email:
            if duplicate_context == "profile":
                raise ValueError("Email ID is already being used by another account.")
            raise ValueError("Email ID is already registered.")

        if mobile_number and existing_user.mobile_number == mobile_number:
            if duplicate_context == "profile":
                raise ValueError("Mobile number is already being used by another account.")
            raise ValueError("Mobile number is already registered.")

        if username and existing_user.username == username:
            if duplicate_context == "profile":
                raise ValueError("Username is already being used by another account.")
            raise ValueError("Username is already registered.")
