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


def _write_log(entity_type: str, entity_id: int | None, action: str, summary: str | None = None, meta: dict | None = None):
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


def _track_model(model_cls, entity_name: str, watched_fields: list[str] | None = None, status_field: str | None = None):
    watched_fields = watched_fields or []

    @event.listens_for(model_cls, "after_insert")
    def _after_insert(mapper, connection, target):  # noqa
        _write_log(
            entity_type=entity_name,
            entity_id=getattr(target, "id", None),
            action="created",
            summary=f"{entity_name} created",
            meta={"fields": {f: _safe_str(getattr(target, f, None)) for f in watched_fields}},
        )

    @event.listens_for(model_cls, "after_update")
    def _after_update(mapper, connection, target):  # noqa
        insp = inspect(target)

        changes = {}
        for attr in watched_fields:
            if attr in insp.attrs and insp.attrs[attr].history.has_changes():
                hist = insp.attrs[attr].history
                old = hist.deleted[0] if hist.deleted else None
                new = hist.added[0] if hist.added else None
                changes[attr] = {"old": _safe_str(old), "new": _safe_str(new)}

        # Special: status changes become a separate “status_changed” action
        if status_field and status_field in insp.attrs and insp.attrs[status_field].history.has_changes():
            hist = insp.attrs[status_field].history
            old = hist.deleted[0] if hist.deleted else None
            new = hist.added[0] if hist.added else None
            _write_log(
                entity_type=entity_name,
                entity_id=getattr(target, "id", None),
                action="status_changed",
                summary=f"{entity_name} status: {_safe_str(old)} → {_safe_str(new)}",
                meta={"field": status_field, "old": _safe_str(old), "new": _safe_str(new)},
            )

        if changes:
            _write_log(
                entity_type=entity_name,
                entity_id=getattr(target, "id", None),
                action="updated",
                summary=f"{entity_name} updated",
                meta={"changes": changes},
            )


def init_audit(app):
    """
    Call this once inside create_app(app).
    It:
      1) captures request context (who is acting)
      2) registers SQLAlchemy model listeners
    """
    from flask import request
    from flask_login import current_user
    from app.audit_context import set_audit_context

    @app.before_request
    def _capture_actor():
        role = (getattr(current_user, "role", "") or "").lower() if hasattr(current_user, "is_authenticated") and current_user.is_authenticated else None
        set_audit_context({
            "user_id": getattr(current_user, "id", None) if hasattr(current_user, "is_authenticated") and current_user.is_authenticated else None,
            "username": getattr(current_user, "username", None) if hasattr(current_user, "is_authenticated") and current_user.is_authenticated else None,
            "role": role,
            "ip": request.headers.get("X-Forwarded-For", request.remote_addr),
            "ua": (request.user_agent.string or "")[:255],
        })

    # Import models ONLY here (prevents circular imports)
    from app.models.procurement_request import ProcurementRequest
    from app.models.vendor import Vendor
    from app.models.payment import Payment
    from app.models.procurement_quotation import ProcurementQuotation

    # Track important fields (safe, minimal)
    _track_model(
        ProcurementRequest,
        "ProcurementRequest",
        watched_fields=["item", "description", "quantity", "amount", "vendor_id", "is_urgent", "status"],
        status_field="status",
    )
    _track_model(
        Vendor,
        "Vendor",
        watched_fields=["name", "phone", "email", "bank_name", "account_name", "account_number"],
        status_field=None,
    )
    _track_model(
        Payment,
        "Payment",
        watched_fields=["amount", "amount_paid", "paid_by_role", "paid_by_name", "receipt_url", "status", "notes", "paid_at"],
        status_field="status",
    )
    _track_model(
        ProcurementQuotation,
        "ProcurementQuotation",
        watched_fields=["procurement_request_id", "file_path", "created_at"],
        status_field=None,
    )
