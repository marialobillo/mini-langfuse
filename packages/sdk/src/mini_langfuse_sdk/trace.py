from functools import wraps, partial
import time
import logging
import inspect
from typing import Any, Callable
import uuid
from datetime import datetime, timezone
from mini_langfuse_sdk._capture import Tracer, _current_trace_id, _current_span_id
from mini_langfuse_sdk._capture import build_error, safe_capture
from mini_langfuse_sdk.tracer import default_tracer

logger = logging.getLogger(__name__)

def trace(
    func: Callable[..., Any] | None = None,
    *,
    tracer: Tracer | None = None,
) -> Callable[..., Any]:
    if func is None:
        return partial(trace, tracer=tracer)
    if tracer is None:
        tracer = default_tracer
    
    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
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
            output = None
            error = None

            try:
                output = await func(*args, **kwargs)
                return output
            except Exception as e:
                error = build_error(e)
                raise
            finally:
                latency_ms = (time.perf_counter() - start) * 1000
                safe_capture(tracer, {
                        "trace_id": trace_id,
                        "span_id": span_id,
                        "parent_span_id": parent_span_id,
                        "name": getattr(func, "__name__", "<unknown>"),
                        "input": {"args": args, "kwargs": kwargs},
                        "output": output,
                        "latency_ms": latency_ms,
                        "started_at": started_at, 
                        "error": error,
                    })
                _current_span_id.reset(token_span)
                _current_trace_id.reset(token_trace)

        return async_wrapper

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
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
                "trace_id": trace_id,
                "span_id": span_id,
                "parent_span_id": parent_span_id,
                "name": getattr(func, "__name__", "<unknown>"),
                "input": {"args": args, "kwargs": kwargs},
                "output": output,
                "latency_ms": latency_ms,
                "started_at": started_at,
                "error": error,
            })
            _current_span_id.reset(token_span)
            _current_trace_id.reset(token_trace)

    return sync_wrapper
