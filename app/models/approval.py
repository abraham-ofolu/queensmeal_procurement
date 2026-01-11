from datetime import datetime
from app.extensions import db


class ApprovalAction(db.Model):
    __tablename__ = "approval_actions"

    id = db.Column(db.Integer, primary_key=True)
    procurement_request_id = db.Column(
        db.Integer,
        db.ForeignKey("procurement_requests.id"),
        nullable=False
    )

    actor = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # approved / rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
