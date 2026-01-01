import os


class Config:
    # Basic
    SECRET_KEY = os.getenv("SECRET_KEY", "queensmeal-secret")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://localhost/queensmeal_procurement"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

    # Business limits (PASS 1: keep one limit, do not expand)
    FINANCE_PAYMENT_LIMIT = float(os.getenv("FINANCE_PAYMENT_LIMIT", "250000"))
