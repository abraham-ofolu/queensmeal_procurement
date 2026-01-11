from datetime import datetime
from app.extensions import db


class ApprovalAction(db.Model):
    __tablename__ = "approval_actions"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)

    request_id = db.Column(
        db.Integer,
        db.ForeignKey("procurement_requests.id"),
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
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
