from sqlalchemy import event, inspect
from app.extensions import db
from app.audit_context import get_audit_context
from app.models.audit_log import AuditLog


def _safe_str(v):
    if v is None:
        return None
    try:
        return str(v)
    except Exception:
        return None


def _write_log(entity_type, entity_id, action, summary=None, meta=None):
    ctx = get_audit_context()

    log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        summary=summary,
        actor_user_id=ctx.get("user_id"),
        actor_username=ctx.get("username"),
        actor_role=ctx.get("role"),
        ip_address=ctx.get("ip"),
        user_agent=ctx.get("ua"),
        meta=meta or None,
    )
    db.session.add(log)


def _track_model(model_cls, entity_name, watched_fields=None, status_field=None):
    watched_fields = watched_fields or []

    @event.listens_for(model_cls, "after_insert")
    def after_insert(mapper, connection, target):
        _write_log(
            entity_name,
            getattr(target, "id", None),
            "created",
            f"{entity_name} created",
        )

    @event.listens_for(model_cls, "after_update")
    def after_update(mapper, connection, target):
        insp = inspect(target)

        if status_field and status_field in insp.attrs:
            hist = insp.attrs[status_field].history
            if hist.has_changes():
                old = hist.deleted[0] if hist.deleted else None
                new = hist.added[0] if hist.added else None
                _write_log(
                    entity_name,
                    getattr(target, "id", None),
                    "status_changed",
                    f"{entity_name} status {old} → {new}",
                )

        changes = {}
        for f in watched_fields:
            if f in insp.attrs and insp.attrs[f].history.has_changes():
                h = insp.attrs[f].history
                changes[f] = {
                    "old": _safe_str(h.deleted[0]) if h.deleted else None,
                    "new": _safe_str(h.added[0]) if h.added else None,
                }

        if changes:
            _write_log(
                entity_name,
                getattr(target, "id", None),
                "updated",
                f"{entity_name} updated",
                meta={"changes": changes},
            )


def init_audit(app):
    from flask import request
    from flask_login import current_user
    from app.audit_context import set_audit_context

    @app.before_request
    def capture_actor():
        if hasattr(current_user, "is_authenticated") and current_user.is_authenticated:
            set_audit_context({
                "user_id": current_user.id,
                "username": getattr(current_user, "username", None),
                "role": getattr(current_user, "role", None),
                "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
                "ua": (request.user_agent.string or "")[:255],
            })
        else:
            set_audit_context({})

    # Import models HERE to avoid circular imports
    from app.models.procurement_request import ProcurementRequest
    from app.models.vendor import Vendor
    from app.models.payment import Payment
    from app.models.procurement_quotation import ProcurementQuotation

    _track_model(
        ProcurementRequest,
        "ProcurementRequest",
        watched_fields=["item", "description", "quantity", "amount", "vendor_id", "is_urgent"],
        status_field="status",
    )

    _track_model(
        Vendor,
        "Vendor",
        watched_fields=["name", "phone", "email", "bank_name", "account_name", "account_number"],
    )

    _track_model(
        Payment,
        "Payment",
        watched_fields=["amount", "amount_paid", "paid_by_role", "paid_by_name", "receipt_url", "notes"],
        status_field="status",
    )

    _track_model(
        ProcurementQuotation,
        "ProcurementQuotation",
        watched_fields=["file_path"],
    )
