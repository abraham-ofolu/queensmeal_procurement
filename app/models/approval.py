from app.extensions import db
from datetime import datetime

class ApprovalAction(db.Model):
    __tablename__ = "approval_actions"

    id = db.Column(db.Integer, primary_key=True)
    procurement_request_id = db.Column(db.Integer, nullable=False)
    actor_id = db.Column(db.Integer, nullable=False)
    actor_role = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # approved / rejected
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
