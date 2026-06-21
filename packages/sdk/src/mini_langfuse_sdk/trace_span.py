import time
import logging
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from mini_langfuse_sdk._capture import build_error, safe_capture, _current_span_id, _current_trace_id
from mini_langfuse_sdk.tracer import default_tracer

logger = logging.getLogger(__name__)


@contextmanager
def trace_span(name, tracer=None):
    tracer = tracer or default_tracer
    span_id = uuid.uuid4().hex

    parent_trace_id = _current_trace_id.get()
    parent_span_id = _current_span_id.get()

    if parent_trace_id is None:
        trace_id = uuid.uuid4().hex
    else:
        trace_id = parent_trace_id

    token_trace = _current_trace_id.set(trace_id)
    token_span = _current_span_id.set(span_id)

    started_at = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    error = None
    
    try:
        yield
    except Exception as e:
        error = build_error(e)
        raise
    finally:
        latency_ms = (time.perf_counter() - start) * 1000
        try:
            safe_capture(tracer, {
                    "trace_id": trace_id,
                    "span_id": span_id,
                    "parent_span_id": parent_span_id,
                    "name": name,
                    "latency_ms": latency_ms,
                    "started_at": started_at,
                    "error": error,
                })
        except Exception:
            logger.warning("Mini-Langfuse: tracer failed to capture span", exc_info=True)
        _current_span_id.reset(token_span)
        _current_trace_id.reset(token_trace)
        