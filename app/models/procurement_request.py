from app.extensions import db
from datetime import datetime

class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(30), default="pending")  
    created_by = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_pending(self):
        return self.status == "pending"

    def approve(self):
        self.status = "approved"

    def reject(self):
        self.status = "rejected"
