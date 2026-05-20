from functools import wraps
from mini_langfuse_sdk.tracer import default_tracer

def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        default_tracer.capture({
            "name": func.__name__, 
            "input": {"args": list(args), "kwargs": kwargs},
            "output": result
        })
        return result
    return wrapper
