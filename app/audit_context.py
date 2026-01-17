"""
Simple request-scoped audit context.
Stores actor info so SQLAlchemy events can access it safely.
"""

from contextvars import ContextVar

_audit_context = ContextVar("audit_context", default={})


def set_audit_context(data: dict):
    _audit_context.set(data or {})


def get_audit_context() -> dict:
    return _audit_context.get() or {}
