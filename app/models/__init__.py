# app/models/__init__.py

# Import models so SQLAlchemy registers them on startup.
# IMPORTANT: If a model is not imported somewhere, its table won't be created by db.create_all().

from app.models.user import User  # noqa: F401
from app.models.vendor import Vendor  # noqa: F401
from app.models.procurement_request import ProcurementRequest  # noqa: F401
from app.models.procurement_quotation import ProcurementQuotation  # noqa: F401
from app.models.payment import Payment  # noqa: F401

# Optional / if you actually use these models elsewhere
# Keep them only if the files exist and classes match names:
try:
    from app.models.approval import ApprovalAction  # noqa: F401
except Exception:
    pass

try:
    from app.models.audit_log import AuditLog  # noqa: F401
except Exception:
    pass
