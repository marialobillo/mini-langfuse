from functools import wraps

def trace(func):
    @wraps
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
