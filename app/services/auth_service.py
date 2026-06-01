from datetime import datetime
from time import time

from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.user import User
from app.utils.helpers import normalize_email, normalize_mobile


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

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        raise ValueError("Username or email already exists.")

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
        delete_flag="N",
    )
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(login_identifier, password):
    identifier = (login_identifier or "").strip()
    if not identifier or not password:
        raise ValueError("Username/email and password are required.")

    user = User.query.filter(
        (User.username == identifier) | (User.email == normalize_email(identifier))
    ).first()

    if not user or not check_password_hash(user.password_hash, password):
        raise ValueError("Invalid login credentials.")

    if user.delete_flag == "Y":
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

    conflicting_user = User.query.filter(
        ((User.username == username) | (User.email == email)) & (User.id != user.id)
    ).first()
    if conflicting_user:
        raise ValueError("Username or email is already being used by another account.")

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
