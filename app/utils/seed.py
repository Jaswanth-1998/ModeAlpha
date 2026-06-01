from datetime import date

from werkzeug.security import generate_password_hash

from app.config.settings import BaseConfig
from app.extensions import db
from app.models.user import User


def seed_default_admin():
    admin = User.query.filter_by(role="admin").first()
    if admin:
        return admin

    admin = User(
        username=BaseConfig.DEFAULT_ADMIN_USERNAME,
        email=BaseConfig.DEFAULT_ADMIN_EMAIL,
        mobile_number=BaseConfig.DEFAULT_ADMIN_MOBILE,
        date_of_birth=date(1990, 1, 1),
        password_hash=generate_password_hash(BaseConfig.DEFAULT_ADMIN_PASSWORD),
        role="admin",
        is_approved=True,
        is_active=True,
        delete_flag="N",
    )
    db.session.add(admin)
    db.session.commit()
    return admin
