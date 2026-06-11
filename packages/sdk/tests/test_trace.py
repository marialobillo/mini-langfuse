import pytest
import time
from mini_langfuse_sdk import trace
from mini_langfuse_sdk.tracer import InMemoryTracer, default_tracer

class BrokenTracer:
    def capture(self, record):
        raise RuntimeError("backend is down")

class FakeTracer:
    def __init__(self):
        self.captured = []
    def capture(self, record):
        self.captured.append(record)


@pytest.fixture(autouse=True)
def clean_tracer():
    default_tracer.records.clear()
    yield


def test_decorated_function_returns_same_value():
    original_func = lambda: 12
    traced_func = trace(original_func)
    assert traced_func() == 12

def test_decorated_function_works_with_positional_arguments():
    original_func = lambda a, b: a * b 
    traced_func = trace(original_func)
    assert traced_func(2,3) == 6

def test_decorated_function_works_with_keyword_arguments():
    original_func = lambda a, b: a * b
    traced_func = trace(original_func)
    assert traced_func(a=2,b=3) == 6

def test_trace_preserves_function_metadata():
    def my_function():
        return 42
    
    traced = trace(my_function)
    assert traced.__name__ == "my_function"

def test_tracer_captures_function_name():
    @trace
    def my_function():
        return 42
    
    my_function()

    assert default_tracer.records[-1]["name"] == "my_function"

def test_trace_captures_positional_input():
    @trace
    def add(a, b):
        return a + b
    
    add(2, 3)
    assert default_tracer.records[-1]["input"] == {"args": (2, 3), "kwargs": {}}

def test_trace_captures_output():
    @trace
    def add(a, b):
        return a + b
    
    add(2, 3)
    assert default_tracer.records[-1]["output"] == 5

def test_trace_captures_latency():
    @trace
    def my_function():
        time.sleep(0.05)
        return 42
    
    my_function()
    latency = default_tracer.records[-1]["latency_ms"]
    assert isinstance(latency, float)
    assert latency >= 0

def test_trace_captures_started_at():
    @trace
    def my_function():
        return 42
    
    my_function()

    started_at = default_tracer.records[-1]["started_at"]
    assert isinstance(started_at, str)
    assert started_at.endswith("+00:00")

def test_trace_sets_error_none_on_success():
    @trace
    def my_function():
        return 42
    
    my_function()

    record = default_tracer.records[-1]
    assert record["error"] is None

def test_trace_propagates_exception():
    @trace
    def my_function():
        raise ValueError("boom")
    
    with pytest.raises(ValueError):
        my_function()

def test_trace_captures_error_details():
    @trace
    def my_function():
        raise ValueError("boom")
    
    with pytest.raises(ValueError):
        my_function()
    
    record = default_tracer.records[-1]
    assert record["error"]["type"] == "ValueError"
    assert record["error"]["message"] == "boom"

def test_trace_records_latency_on_failure():
    @trace
    def my_function():
        raise ValueError("boom")
    
    with pytest.raises(ValueError):
        my_function()

    record = default_tracer.records[-1]
    assert isinstance(record["latency_ms"], float)
    assert record["latency_ms"] >= 0

def test_trace_preserves_original_exception():
    @trace
    def my_function():
        raise ValueError("boom")

    with pytest.raises(ValueError) as exc_info:
        my_function()

    assert str(exc_info.value) == "boom"

def test_trace_uses_injected_tracer():
    fake = FakeTracer()

    @trace(tracer=fake)
    def my_function(a, b):
        return a + b
    
    my_function(2, 3)

    assert len(fake.captured) == 1
    assert fake.captured[0]["name"] == "my_function"
    assert fake.captured[0]["output"] == 5

def test_trace_silently_swallows_tracer_failure():
    broken = BrokenTracer()

    @trace(tracer=broken)
    def my_function():
        return 42

    result = my_function()
    assert result == 42

def test_trace_logs_warning_when_tracer_fails(caplog):
    broken = BrokenTracer()

    @trace(tracer=broken)
    def my_function():
        return 42
    
    result = my_function()
    assert result == 42
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    assert "tracer" in caplog.records[0].message.lower()

@pytest.mark.anyio
async def test_decorated_async_function_returns_same_value():
    tracer = InMemoryTracer()
    
    @trace(tracer=tracer)
    async def my_async_function():
        return 42
    
    result = await my_async_function()
    assert result == 42

@pytest.mark.anyio
async def test_trace_captures_resolved_output_for_async_function():
    tracer = InMemoryTracer()

    @trace(tracer=tracer)
    async def my_async_function():
        return 42

    await my_async_function()

    assert tracer.records[-1]["output"] == 42

@pytest.mark.anyio
async def test_trace_measures_real_latency_for_async_function():
    import asyncio

    tracer = InMemoryTracer()

    @trace(tracer=tracer)
    async def slow_async_function():
        await asyncio.sleep(0.05)   # 50 ms
        return "done"

    await slow_async_function()

    latency = tracer.records[-1]["latency_ms"]
    assert latency >= 40

@pytest.mark.anyio
async def test_trace_async_captures_and_propagates_exception():
    tracer = InMemoryTracer()

    @trace(tracer=tracer)
    async def failing_async_function():
        raise ValueError("async boom")

    with pytest.raises(ValueError):
        await failing_async_function()

    record = tracer.records[-1]
    assert record["error"] == {"type": "ValueError", "message": "async boom"}