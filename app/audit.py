from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

from flask import g, request
from flask_login import current_user
from sqlalchemy import event, inspect

from app.extensions import db


def _safe_actor() -> Dict[str, Any]:
    """
    Build actor context safely (works even if no request context or user not logged in).
    """
    actor = {
        "user_id": None,
        "role": None,
        "name": None,
        "ip": None,
        "user_agent": None,
    }

    try:
        # request context may not exist in some edge cases
        actor["ip"] = request.headers.get("X-Forwarded-For", "").split(",")[0].strip() or request.remote_addr
        actor["user_agent"] = request.headers.get("User-Agent")
    except Exception:
        pass

    try:
        if getattr(current_user, "is_authenticated", False):
            actor["user_id"] = getattr(current_user, "id", None)
            actor["role"] = getattr(current_user, "role", None)
            # your User model might have full_name/name/username
            actor["name"] = (
                getattr(current_user, "full_name", None)
                or getattr(current_user, "name", None)
                or getattr(current_user, "username", None)
            )
    except Exception:
        pass

    return actor


def _to_jsonable(value: Any) -> Any:
    """
    Convert values to JSON-safe forms.
    """
    if isinstance(value, (datetime,)):
        return value.isoformat()
    try:
        json.dumps(value)
        return value
    except Exception:
        return str(value)


def _extract_changes(obj: Any) -> Dict[str, Dict[str, Any]]:
    """
    Return {"field": {"old": ..., "new": ...}} for updated fields.
    """
    changes: Dict[str, Dict[str, Any]] = {}
    state = inspect(obj)

    for attr in state.mapper.column_attrs:
        key = attr.key
        hist = state.attrs[key].history
        if not hist.has_changes():
            continue

        old_val = hist.deleted[0] if hist.deleted else None
        new_val = hist.added[0] if hist.added else getattr(obj, key, None)

        changes[key] = {
            "old": _to_jsonable(old_val),
            "new": _to_jsonable(new_val),
        }

    return changes


def init_audit(app) -> None:
    """
    Initializes audit trail hooks. Safe + idempotent.

    - Adds request actor context in flask.g
    - Adds SQLAlchemy session hook to create AuditLog rows for tracked models
    """
    # Prevent double-registration (Render reloads, etc.)
    if getattr(app, "_AUDIT_INITIALIZED", False):
        return
    app._AUDIT_INITIALIZED = True

    # Import here to avoid circular imports at module import time
    from app.models.audit_log import AuditLog

    # Track these models (import inside try so app won't crash if a model path changes)
    tracked_classes = []
    try:
        from app.models.procurement_request import ProcurementRequest
        tracked_classes.append(ProcurementRequest)
    except Exception:
        pass
    try:
        from app.models.procurement_quotation import ProcurementQuotation
        tracked_classes.append(ProcurementQuotation)
    except Exception:
        pass
    try:
        from app.models.payment import Payment
        tracked_classes.append(Payment)
    except Exception:
        pass
    try:
        from app.models.vendor import Vendor
        tracked_classes.append(Vendor)
    except Exception:
        pass
    try:
        from app.models.user import User
        tracked_classes.append(User)
    except Exception:
        pass

    tracked_tuple = tuple(tracked_classes)

    @app.before_request
    def _audit_before_request():
        # Store actor on g for the current request
        g.audit_actor = _safe_actor()

    def _get_actor_from_g() -> Dict[str, Any]:
        try:
            return getattr(g, "audit_actor", None) or _safe_actor()
        except Exception:
            return _safe_actor()

    def _is_tracked(obj: Any) -> bool:
        if not tracked_tuple:
            return False
        return isinstance(obj, tracked_tuple)

    def _entity_type(obj: Any) -> str:
        return obj.__class__.__name__

    def _entity_id(obj: Any) -> Optional[str]:
        try:
            val = getattr(obj, "id", None)
            return str(val) if val is not None else None
        except Exception:
            return None

    # IMPORTANT:
    # Adding objects inside flush can cause recursion, so we guard using session.info flag.
    def _after_flush(session, flush_context):
        if session.info.get("_audit_skip", False):
            return

        logs = []
        actor = _get_actor_from_g()

        # New objects
        for obj in list(session.new):
            if isinstance(obj, AuditLog):
                continue
            if not _is_tracked(obj):
                continue
            logs.append(
                AuditLog(
                    entity_type=_entity_type(obj),
                    entity_id=_entity_id(obj),
                    action="create",
                    changes={},  # for create we can keep empty or snapshot later
                    actor_user_id=actor.get("user_id"),
                    actor_role=actor.get("role"),
                    actor_name=actor.get("name"),
                    ip_address=actor.get("ip"),
                    user_agent=actor.get("user_agent"),
                    created_at=datetime.utcnow(),
                )
            )

        # Updated objects
        for obj in list(session.dirty):
            if isinstance(obj, AuditLog):
                continue
            if not _is_tracked(obj):
                continue
            if not session.is_modified(obj, include_collections=False):
                continue

            changes = _extract_changes(obj)
            if not changes:
                continue

            logs.append(
                AuditLog(
                    entity_type=_entity_type(obj),
                    entity_id=_entity_id(obj),
                    action="update",
                    changes=changes,
                    actor_user_id=actor.get("user_id"),
                    actor_role=actor.get("role"),
                    actor_name=actor.get("name"),
                    ip_address=actor.get("ip"),
                    user_agent=actor.get("user_agent"),
                    created_at=datetime.utcnow(),
                )
            )

        # Deleted objects
        for obj in list(session.deleted):
            if isinstance(obj, AuditLog):
                continue
            if not _is_tracked(obj):
                continue
            logs.append(
                AuditLog(
                    entity_type=_entity_type(obj),
                    entity_id=_entity_id(obj),
                    action="delete",
                    changes={},
                    actor_user_id=actor.get("user_id"),
                    actor_role=actor.get("role"),
                    actor_name=actor.get("name"),
                    ip_address=actor.get("ip"),
                    user_agent=actor.get("user_agent"),
                    created_at=datetime.utcnow(),
                )
            )

        if not logs:
            return

        # Prevent recursion: add logs once, then skip if flush happens again
        session.info["_audit_skip"] = True
        try:
            session.add_all(logs)
        finally:
            session.info["_audit_skip"] = False

    # Hook into Flask-SQLAlchemy session
    # db.session is a scoped_session, but event works on it
    event.listen(db.session, "after_flush", _after_flush)
