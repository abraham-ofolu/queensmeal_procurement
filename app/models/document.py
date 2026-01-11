from datetime import datetime
from app.extensions import db


class Document(db.Model):
    __tablename__ = "documents"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)

    related_type = db.Column(
        db.String(50),
        nullable=False
    )  # e.g. "procurement", "payment"

    related_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    filename = db.Column(
        db.String(255),
        nullable=False
    )

    file_path = db.Column(
        db.String(500),
        nullable=False
    )

    uploaded_by = db.Column(
        db.String(100),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
