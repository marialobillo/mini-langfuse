from mini_langfuse_sdk import InMemoryTracer

def test_tracer_records_what_it_captures():
    tracer = InMemoryTracer()
    tracer.capture({"name": "foo"})
    assert tracer.records == [{"name": "foo"}]