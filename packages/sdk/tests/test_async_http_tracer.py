import pytest
import logging
import httpx
import asyncio

from mini_langfuse_sdk import AsyncHTTPTracer

class FakeClient:
    def __init__(self):
        self.calls = []

    def post(self, url, json, headers=None):
        self.calls.append({"url": url, "json": json, "headers": headers})


@pytest.mark.anyio
async def test_async_tracer_capture_does_not_post_immediately():
    fake = FakeClient()
    tracer = AsyncHTTPTracer(
        url="http://example.com/traces",
        api_key="test-key",
        client=fake,
    )

    tracer.capture({"name": "foo"})

    assert fake.calls == []

@pytest.mark.anyio
async def test_async_tracer_flush_sends_all_buffered_records_in_one_post():
    fake = FakeClient()
    tracer = AsyncHTTPTracer(
        url="http://example.com/traces",
        api_key="test-key",
        client=fake,
    )

    tracer.capture({"name": "first"})
    tracer.capture({"name": "second"})
    tracer.capture({"name": "third"})

    await tracer.flush()

    assert len(fake.calls) == 1
    assert fake.calls[0]["json"] == [
        {"name": "first"},
        {"name": "second"},
        {"name": "third"},
    ]

@pytest.mark.anyio
async def test_async_tracer_flush_does_nothing_when_buffer_is_empty():
    fake = FakeClient()
    tracer = AsyncHTTPTracer(
        url="http://example.com/traces",
        api_key="test-key",
        client=fake,
    )

    await tracer.flush()

    assert fake.calls == []

@pytest.mark.anyio
async def test_async_tracer_flush_silently_swallows_post_failure(caplog):
    class FailingClient:
        def post(self, url, json, headers=None):
            raise httpx.ConnectError("connection refused")

    tracer = AsyncHTTPTracer(
        url="http://example.com/traces",
        api_key="test-key",
        client=FailingClient(),
    )

    tracer.capture({"name": "foo"})

    with caplog.at_level(logging.WARNING):
        await tracer.flush()

    assert any(
        record.levelname == "WARNING"
        for record in caplog.records
    )

@pytest.mark.anyio
async def test_async_tracer_flushes_automatically_when_batch_size_reached():
    fake = FakeClient()
    tracer = AsyncHTTPTracer(
        url="http://example.com/traces",
        api_key="test-key",
        client=fake,
        batch_size=3,
    )
    await tracer.start()

    tracer.capture({"name": "first"})
    tracer.capture({"name": "second"})
    tracer.capture({"name": "third"})

    await asyncio.sleep(0.5)

    assert len(fake.calls) == 1
    assert fake.calls[0]["json"] == [
        {"name": "first"},
        {"name": "second"},
        {"name": "third"},
    ]

    await tracer.stop()