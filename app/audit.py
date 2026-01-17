from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict

from flask import g, has_request_context, request
from flask_login import current_user
from sqlalchemy import text
from sqlalchemy import inspect as sa_inspect

from app.extensions import db


def _actor_payload() -> Dict[str, Any]:
    """
    Returns best-effort actor context.
    Must NEVER crash app if auth/request isn't available.
    """
    payload: Dict[str, Any] = {
        "actor_user_id": None,
        "actor_role": None,
        "actor_name": None,
        "ip_address": None,
        "user_agent": None,
    }

    try:
        if has_request_context():
            payload["ip_address"] = request.headers.get("X-Forwarded-For", request.remote_addr)
            payload["user_agent"] = request.headers.get("User-Agent")
    except Exception:
        pass

    try:
        if hasattr(current_user, "is_authenticated") and current_user.is_authenticated:
            payload["actor_user_id"] = getattr(current_user, "id", None)
            payload["actor_role"] = (getattr(current_user, "role", None) or "").lower() or None
            payload["actor_name"] = getattr(current_user, "username", None) or getattr(current_user, "name", None) or None
    except Exception:
        pass

    # If you ever store extra actor info in g, respect it
    try:
        if has_request_context():
            payload["actor_role"] = getattr(g, "actor_role", payload["actor_role"])
            payload["actor_name"] = getattr(g, "actor_name", payload["actor_name"])
    except Exception:
        pass

    return payload


def _safe_insert(connection, payload: Dict[str, Any]) -> None:
    """
    Tries to insert audit row with full columns.
    If DB schema differs, it falls back to minimal insert that still satisfies NOT NULL constraints.
    This must NEVER crash your app.
    """
    # Ensure legacy required columns are always present
    entity = payload.get("entity") or payload.get("entity_type") or "Unknown"
    action = payload.get("action") or "unknown"

    payload["entity"] = entity
    payload["action"] = action

    # Convert changes safely
    changes_val = payload.get("changes")
    if isinstance(changes_val, (dict, list)):
        try:
            payload["changes_json"] = json.dumps(changes_val)
        except Exception:
            payload["changes_json"] = "{}"
    elif isinstance(changes_val, str):
        payload["changes_json"] = changes_val
    else:
        payload["changes_json"] = "{}"

    payload["created_at"] = payload.get("created_at") or datetime.utcnow()

    # Attempt 1: full insert (new schema)
    try:
        connection.execute(
            text(
                """
                INSERT INTO audit_logs
                (entity, entity_type, entity_id, action, changes, actor_user_id, actor_role, actor_name, ip_address, user_agent, created_at)
                VALUES
                (:entity, :entity_type, :entity_id, :action, CAST(:changes_json AS JSON), :actor_user_id, :actor_role, :actor_name, :ip_address, :user_agent, :created_at)
                """
            ),
            payload,
        )
        return
    except Exception:
        pass

    # Attempt 2: without JSON cast
    try:
        connection.execute(
            text(
                """
                INSERT INTO audit_logs
                (entity, entity_type, entity_id, action, changes, actor_user_id, actor_role, actor_name, ip_address, user_agent, created_at)
                VALUES
                (:entity, :entity_type, :entity_id, :action, :changes_json, :actor_user_id, :actor_role, :actor_name, :ip_address, :user_agent, :created_at)
                """
            ),
            payload,
        )
        return
    except Exception:
        pass

    # Attempt 3: legacy minimal columns (guaranteed to exist in your DB)
    try:
        connection.execute(
            text(
                """
                INSERT INTO audit_logs (entity, action, created_at)
                VALUES (:entity, :action, :created_at)
                """
            ),
            {"entity": entity, "action": action, "created_at": payload["created_at"]},
        )
    except Exception:
        # Worst case: do nothing (never crash the business app)
        return


def _get_pk_str(target: Any) -> str | None:
    try:
        insp = sa_inspect(target)
        if insp.identity and len(insp.identity) > 0:
            return str(insp.identity[0])
    except Exception:
        pass
    return None


def _changes_dict(target: Any) -> Dict[str, Any]:
    """
    Best-effort change capture.
    For inserts we typically don't have 'history' yet, so this stays small.
    """
    try:
        insp = sa_inspect(target)
        changes: Dict[str, Any] = {}
        for attr in insp.mapper.column_attrs:
            key = attr.key
            # avoid huge blobs
            if key in ("password_hash",):
                continue
            try:
                val = getattr(target, key, None)
                if isinstance(val, (str, int, float, bool)) or val is None:
                    changes[key] = val
            except Exception:
                continue
        return changes
    except Exception:
        return {}


def init_audit(app) -> None:
    """
    Hooks into SQLAlchemy and logs create/update/delete for key models.
    IMPORTANT: This MUST NEVER break the app even if schema changes.
    """
    from sqlalchemy import event

    # Track only your important business entities
    TRACKED_MODELS = {
        "ProcurementRequest",
        "Vendor",
        "Payment",
        "ProcurementQuotation",
        "User",
    }

    def should_track(target: Any) -> bool:
        try:
            return target.__class__.__name__ in TRACKED_MODELS
        except Exception:
            return False

    def make_payload(target: Any, action: str) -> Dict[str, Any]:
        actor = _actor_payload()
        entity_type = target.__class__.__name__
        return {
            "entity": entity_type,               # satisfy legacy NOT NULL
            "entity_type": entity_type,
            "entity_id": _get_pk_str(target),
            "action": action,
            "changes": _changes_dict(target),
            **actor,
            "created_at": datetime.utcnow(),
        }

    @event.listens_for(db.session, "after_flush")
    def receive_after_flush(session, flush_context):
        # Log inserts/updates/deletes after flush so PK exists
        try:
            connection = session.connection()
        except Exception:
            return

        # INSERTS
        for obj in list(session.new):
            if not should_track(obj):
                continue
            try:
                _safe_insert(connection, make_payload(obj, "create"))
            except Exception:
                continue

        # UPDATES
        for obj in list(session.dirty):
            if not should_track(obj):
                continue
            try:
                _safe_insert(connection, make_payload(obj, "update"))
            except Exception:
                continue

        # DELETES
        for obj in list(session.deleted):
            if not should_track(obj):
                continue
            try:
                _safe_insert(connection, make_payload(obj, "delete"))
            except Exception:
                continue
