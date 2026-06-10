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