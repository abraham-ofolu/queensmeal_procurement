import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")

    # Explicit DB resolution (Render-safe)
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("SQLALCHEMY_DATABASE_URI")
        or os.environ.get("DATABASE_URL")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
