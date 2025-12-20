from app.extensions import db

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Identity
    company_name = db.Column(db.String(200), nullable=False)
    vendor_type = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text, nullable=True)

    # Contact
    contact_person = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=True)

    # Finance
    bank_name = db.Column(db.String(100), nullable=True)
    account_name = db.Column(db.String(100), nullable=True)
    account_number = db.Column(db.String(30), nullable=True)

    # Compliance
    cac_number = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(20), default="pending")
