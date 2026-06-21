import pytest
from mini_langfuse_sdk import trace, trace_span, InMemoryTracer

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

def test_trace_span_captures_span_id():
    tracer = InMemoryTracer()

    with trace_span("foo", tracer=tracer):
        pass

    record = tracer.records[-1]
    assert "span_id" in record
    assert isinstance(record["span_id"], str)
    assert len(record["span_id"]) > 0

def test_trace_span_generates_unique_span_ids():
    tracer = InMemoryTracer()

    with trace_span("foo", tracer=tracer):
        pass
    with trace_span("foo", tracer=tracer):
        pass

    first_span_id = tracer.records[-2]["span_id"]
    second_span_id = tracer.records[-1]["span_id"]

    assert first_span_id != second_span_id

def test_trace_span_captures_trace_id_for_root_span():
    tracer = InMemoryTracer()

    with trace_span("root", tracer=tracer):
        pass

    record = tracer.records[-1]
    assert "trace_id" in record
    assert isinstance(record["trace_id"], str)
    assert len(record["trace_id"]) > 0

def test_nested_spans_share_trace_id():
    tracer = InMemoryTracer()

    with trace_span("parent", tracer=tracer):
        with trace_span("child", tracer=tracer):
            pass

    parent_record = tracer.records[0]
    child_record = tracer.records[1]

    assert parent_record["trace_id"] == child_record["trace_id"]

def test_root_span_has_no_parent_span_id():
    tracer = InMemoryTracer()

    with trace_span("root", tracer=tracer):
        pass

    record = tracer.records[-1]
    assert record["parent_span_id"] is None

def test_nested_span_has_parent_span_id_from_parent():
    tracer = InMemoryTracer()

    with trace_span("parent", tracer=tracer):
        with trace_span("child", tracer=tracer):
            pass

    child_record = tracer.records[0]
    parent_record = tracer.records[1]

    assert child_record["parent_span_id"] == parent_record["span_id"]
    assert parent_record["parent_span_id"] is None

def test_trace_captures_trace_id_span_id_and_parent_span_id():
    tracer = InMemoryTracer()

    @trace(tracer=tracer)
    def my_function():
        return 42

    my_function()

    record = tracer.records[-1]
    assert isinstance(record["trace_id"], str)
    assert len(record["trace_id"]) > 0
    assert isinstance(record["span_id"], str)
    assert len(record["span_id"]) > 0
    assert record["parent_span_id"] is None