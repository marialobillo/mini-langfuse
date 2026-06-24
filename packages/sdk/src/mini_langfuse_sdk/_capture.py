import logging
from contextvars import ContextVar
from typing import Any, Protocol

logger = logging.getLogger(__name__)

class Tracer(Protocol):
    def capture(self, record: dict[str, Any]) -> None: ...

_current_trace_id: ContextVar[str | None] = ContextVar("current_trace_id", default=None)
_current_span_id: ContextVar[str | None] = ContextVar("current_span_id", default=None)

def build_error(exc: Exception) -> dict:
    """Build the error dict captured in a trace record."""
    return {"type": type(exc).__name__, "message": str(exc)}


def safe_capture(tracer: Tracer, record: dict[str, Any]) -> None:
    """Capture a record swallowing tracer failures and logging a warning."""
    try:
        tracer.capture(record)
    except Exception:
        logger.warning("Mini-Langfuse: tracer failed to capture record", exc_info=True)