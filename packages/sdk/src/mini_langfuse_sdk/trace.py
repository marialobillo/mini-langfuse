from functools import wraps
import time
from datetime import datetime, timezone
from mini_langfuse_sdk.tracer import default_tracer


def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        started_at = datetime.now(timezone.utc).isoformat()

        output = None
        error = None

        try:
            output = func(*args, **kwargs)
            return output
        except Exception as e:
            error = {"type": type(e).__name__, "message": str(e)}
            raise
        finally:
            latency_ms = (time.perf_counter() - start) * 1000
            default_tracer.capture({
                "name": func.__name__, 
                "input": {"args": list(args), "kwargs": kwargs},
                "output": output,
                "latency_ms": latency_ms,
                "started_at": started_at, 
                "error": error,
            })


    
    return wrapper
