from functools import wraps
import time
from mini_langfuse_sdk.tracer import default_tracer


def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        latency_ms = (time.perf_counter() - start) * 1000
        default_tracer.capture({
            "name": func.__name__, 
            "input": {"args": list(args), "kwargs": kwargs},
            "output": result,
            "latency_ms": latency_ms
        })
        return result
    return wrapper
