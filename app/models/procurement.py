from app.extensions import db

class ProcurementRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(200), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey("vendor.id"))
    created_by = db.Column(db.String(50))
    status = db.Column(db.String(30), default="draft")

    quotation_file = db.Column(db.String(300), nullable=True)

    vendor = db.relationship("Vendor")
