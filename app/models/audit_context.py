from contextvars import ContextVar

_audit_ctx: ContextVar[dict] = ContextVar("audit_ctx", default={})


def set_audit_context(data: dict):
    _audit_ctx.set(data or {})


def get_audit_context() -> dict:
    return _audit_ctx.get() or {}
