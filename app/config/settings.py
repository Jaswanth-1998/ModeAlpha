import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import quote_plus


APP_DIR = Path(__file__).resolve().parents[1]


def build_database_uri():
    explicit_database_url = os.getenv("DATABASE_URL")
    if explicit_database_url:
        if explicit_database_url.startswith("postgres://"):
            return explicit_database_url.replace("postgres://", "postgresql://", 1)
        return explicit_database_url

    postgres_user = os.getenv("POSTGRES_USER", "postgres")
    postgres_password = quote_plus(os.getenv("POSTGRES_PASSWORD", "postgres"))
    postgres_host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_db = os.getenv("POSTGRES_DB", "mock_test")

    return (
        f"postgresql+psycopg2://{postgres_user}:{postgres_password}"
        f"@{postgres_host}:{postgres_port}/{postgres_db}"
    )


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INSTANCE_DIR = APP_DIR / "instance"
    UPLOAD_DIR = INSTANCE_DIR / "uploads"
    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    POSTGRES_MAINTENANCE_DB = os.getenv("POSTGRES_MAINTENANCE_DB", "postgres")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
    DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@mocktest.local")
    DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "Admin@123")
    DEFAULT_ADMIN_MOBILE = os.getenv("DEFAULT_ADMIN_MOBILE", "9999999999")

    @classmethod
    def ensure_directories(cls):
        cls.INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
