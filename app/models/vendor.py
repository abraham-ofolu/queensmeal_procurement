from app.extensions import db
from datetime import datetime

class Vendor(db.Model):
    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    bank_name = db.Column(db.String(120), nullable=False)
    account_name = db.Column(db.String(120), nullable=False)
    account_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
