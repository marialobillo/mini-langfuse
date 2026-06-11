import pytest
from mini_langfuse_sdk import trace_span, InMemoryTracer

def test_trace_span_captures_name():
    tracer = InMemoryTracer()
    with trace_span("my_block", tracer=tracer):
        pass

    assert tracer.records[-1]["name"] == "my_block"

def test_trace_span_captures_latency():
    tracer = InMemoryTracer()
    with trace_span("my_block", tracer=tracer):
        pass

    record = tracer.records[-1]
    assert isinstance(record["latency_ms"], float)
    assert record["latency_ms"] >= 0

def test_trace_span_captures_started_at():
    tracer = InMemoryTracer()
    with trace_span("my_block", tracer=tracer):
        pass

    record = tracer.records[-1]
    assert isinstance(record["started_at"], str)
    assert record["started_at"].endswith("+00:00")

def test_trace_span_sets_error_none_on_success():
    tracer = InMemoryTracer()
    with trace_span("my_block", tracer=tracer):
        pass

    record = tracer.records[-1]
    assert record["error"] is None

def test_trace_span_captures_and_propagates_exception():
    tracer = InMemoryTracer()
    with pytest.raises(ValueError):
        with trace_span("failing_block", tracer=tracer):
            raise ValueError("boom")
    
    record = tracer.records[-1]
    assert record["error"] == {"type": "ValueError", "message": "boom"}

def test_trace_span_uses_injected_tracer():
    injected_tracer = InMemoryTracer()
    with trace_span("foo", tracer=injected_tracer):
        pass

    assert len(injected_tracer.records) == 1

def test_trace_span_silently_swallows_tracer_failure():
    class BrokenTracer:
        def capture(self, record):
            raise RuntimeError("tracer down")
        
    with trace_span("foo", tracer=BrokenTracer()):
        pass

def test_trace_span_logs_warning_when_tracer_fails(caplog):
    import logging

    class BrokenTracer:
        def capture(self, record):
            raise RuntimeError("tracer down")

    with caplog.at_level(logging.WARNING):
        with trace_span("foo", tracer=BrokenTracer()):
            pass

    assert any(
        record.levelname == "WARNING" and "tracer" in record.message.lower()
        for record in caplog.records
    )