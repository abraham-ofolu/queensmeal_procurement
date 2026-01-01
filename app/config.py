# app/config.py
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    # =========================
    # SECURITY
    # =========================
    SECRET_KEY = os.getenv("SECRET_KEY", "queensmeal-secret-change-this")

    # =========================
    # DATABASE
    # =========================
    # Prefer DATABASE_URL (recommended for Postgres):
    # export DATABASE_URL="postgresql+psycopg2://username:password@localhost:5432/queensmeal_procurement"
    #
    # If DATABASE_URL is not set, fallback to local postgres (DB name only)
    # You can also switch fallback to SQLite if you want.
    DATABASE_URL = os.getenv("DATABASE_URL")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL or os.getenv(
        "SQLALCHEMY_DATABASE_URI",
        "postgresql+psycopg2://localhost/queensmeal_procurement",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # =========================
    # UPLOADS (Quotations, etc.)
    # =========================
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(10 * 1024 * 1024)))  # 10MB
    ALLOWED_QUOTATION_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

    # =========================
    # BUSINESS RULES / LIMITS
    # =========================
    # IMPORTANT:
    # I don't want to guess the exact limits you agreed in the SOP.
    # Set them via environment variables to match your SOP exactly.
    #
    # Example:
    # export FINANCE_PAYMENT_LIMIT_NGN="500000"
    # export DIRECTOR_PAYMENT_LIMIT_NGN="999999999"
    #
    # Meaning:
    # - Finance can pay up to FINANCE_PAYMENT_LIMIT_NGN for an APPROVED request.
    # - If above that limit, ONLY director can pay.
    FINANCE_PAYMENT_LIMIT_NGN = float(os.getenv("FINANCE_PAYMENT_LIMIT_NGN", "500000"))
    DIRECTOR_PAYMENT_LIMIT_NGN = float(os.getenv("DIRECTOR_PAYMENT_LIMIT_NGN", "999999999"))

    # =========================
    # UI
    # =========================
    APP_NAME = os.getenv("APP_NAME", "Queensmeal Procurement")
