from datetime import datetime
from app.extensions import db


class Approval(db.Model):
    __tablename__ = "approvals"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)

    procurement_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    actor = db.Column(
        db.String(100),
        nullable=False
    )

    action = db.Column(
        db.String(50),
        nullable=False
    )  # approved / rejected

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
