from datetime import datetime
from app.extensions import db


class Vendor(db.Model):
    __tablename__ = "vendors"

    id = db.Column(db.Integer, primary_key=True)

    # REQUIRED
    name = db.Column(db.String(255), nullable=False)

    # OPTIONAL
    category = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(255))
    notes = db.Column(db.Text)

    # BANK DETAILS
    bank_name = db.Column(db.String(100))
    account_name = db.Column(db.String(255))
    account_number = db.Column(db.String(50))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Vendor {self.name}>"
