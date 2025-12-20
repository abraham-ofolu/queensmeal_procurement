from datetime import datetime
from app.extensions import db

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    entity_type = db.Column(db.String(50))   # e.g. "procurement"
    entity_id = db.Column(db.Integer)

    action = db.Column(db.String(50))        # submit, review, approve, reject, upload_quotation
    performed_by = db.Column(db.String(50))  # username
    role = db.Column(db.String(50))          # role at the time
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
