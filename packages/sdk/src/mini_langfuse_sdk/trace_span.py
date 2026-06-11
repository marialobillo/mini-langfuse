import time
import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from mini_langfuse_sdk._capture import build_error, safe_capture
from mini_langfuse_sdk.tracer import default_tracer

logger = logging.getLogger(__name__)

@contextmanager
def trace_span(name, tracer=None):
    tracer = tracer or default_tracer
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
        safe_capture(tracer, {
                "name": name,
                "latency_ms": latency_ms,
                "started_at": started_at,
                "error": error,
            })
        