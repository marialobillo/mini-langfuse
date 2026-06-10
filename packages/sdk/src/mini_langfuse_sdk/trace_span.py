import time
from contextlib import contextmanager
from datetime import datetime, timezone
from mini_langfuse_sdk.tracer import default_tracer

@contextmanager
def trace_span(name, tracer=None):
    tracer = tracer or default_tracer
    started_at = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    try:
        yield
    finally:
        latency_ms = (time.perf_counter() - start) * 1000
        tracer.capture({
            "name": name,
            "latency_ms": latency_ms,
            "started_at": started_at,
            })