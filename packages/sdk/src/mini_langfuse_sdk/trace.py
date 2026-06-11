from functools import wraps, partial
import time
import logging
from datetime import datetime, timezone
from mini_langfuse_sdk._capture import build_error, safe_capture
from mini_langfuse_sdk.tracer import default_tracer

logger = logging.getLogger(__name__)

def trace(func=None, *, tracer=None):
    if func is None:
        return partial(trace, tracer=tracer)
    if tracer is None:
        tracer = default_tracer
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        started_at = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()
        
        output = None
        error = None

        try:
            output = func(*args, **kwargs)
            return output
        except Exception as e:
            error = build_error(e)
            raise
        finally:
            latency_ms = (time.perf_counter() - start) * 1000
            safe_capture(tracer, {
                    "name": func.__name__, 
                    "input": {"args": args, "kwargs": kwargs},
                    "output": output,
                    "latency_ms": latency_ms,
                    "started_at": started_at, 
                    "error": error,
                })

    return wrapper
