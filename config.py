import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Prefer Render Postgres if present
    db_url = os.environ.get("DATABASE_URL")

    # Render sometimes provides postgres:// which SQLAlchemy may reject; normalize it
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
