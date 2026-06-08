import httpx
import pytest
import logging
from mini_langfuse_sdk import HTTPTracer, trace

class FakeClient:
    def __init__(self):
        self.calls = []

    def post(self, url, json, headers=None):
        self.calls.append({"url": url, "json": json, "headers": headers})


class FailingClient:
    def post(self, url, json, headers=None):
        raise httpx.ConnectError("connection refused")


def test_http_tracer_posts_record_as_json():
    fake = FakeClient()
    tracer = HTTPTracer(url="http://localhost:8000/traces", client=fake)

    tracer.capture({"name": "foo"})

    assert len(fake.calls) == 1
    assert fake.calls[0]["url"] == "http://localhost:8000/traces"
    assert fake.calls[0]["json"] == {"name": "foo"}

def test_http_tracer_propagates_http_errors():
    failing = FailingClient()
    tracer = HTTPTracer(url="http://localhost:8000/traces", client=failing)

    with pytest.raises(httpx.ConnectError):
        tracer.capture({"name": "foo"})

def test_trace_with_http_tracer_posts_to_backend():
    fake = FakeClient()
    http_tracer = HTTPTracer(url="http://localhost:8000/traces", client=fake)

    @trace(tracer=http_tracer)
    def my_function():
        return 42
    
    result = my_function()

    assert result == 42
    assert len(fake.calls) == 1
    posted = fake.calls[0]["json"]
    assert posted["name"] == "my_function"
    assert posted["output"] == 42
    assert posted["error"] is None

def test_http_tracer_uses_configured_url():
    fake = FakeClient()
    tracer = HTTPTracer(url="https://my-custom-host.com/api/traces", client=fake)

    tracer.capture({"name": "foo"})

    assert fake.calls[0]["url"] == "https://my-custom-host.com/api/traces"

def test_http_tracer_reads_url_from_env_var(monkeypatch):
    monkeypatch.setenv("MINI_LANGFUSE_URL", "http://from-env.com/traces")
    fake = FakeClient()

    tracer = HTTPTracer(client=fake)
    tracer.capture({"name": "foo"})

    assert fake.calls[0]["url"] == "http://from-env.com/traces"

def test_http_tracer_explicit_url_wins_over_env_var(monkeypatch):
    monkeypatch.setenv("MINI_LANGFUSE_URL", "http://from-env.com/traces")
    fake = FakeClient()

    tracer = HTTPTracer(url="http://explicit.com/traces", client=fake)
    tracer.capture({"name": "foo"})

    assert fake.calls[0]["url"] == "http://explicit.com/traces"

def test_http_tracer_does_nothing_when_url_is_missing(monkeypatch):
    monkeypatch.delenv("MINI_LANGFUSE_URL", raising=False)
    fake = FakeClient()

    tracer = HTTPTracer(client=fake)

    tracer.capture({"name": "foo"})

    assert fake.calls == []

def test_http_tracer_logs_warning_when_url_is_missing(monkeypatch, caplog):
    monkeypatch.delenv("MINI_LANGFUSE_URL", raising=False)
    with caplog.at_level(logging.WARNING):
        HTTPTracer()

    assert any("url" in record.message.lower() for record in caplog.records)
    assert any(record.levelname == "WARNING" for record in caplog.records)

def test_http_tracer_sends_api_key_in_authorization_header():
    fake = FakeClient()
    tracer = HTTPTracer(
        url="http://example.com/traces",
        api_key="secret-key-123",
        client=fake,
    )
    tracer.capture({"name": "foo"})
    assert fake.calls[0]["headers"] == {"Authorization": "Bearer secret-key-123"}

def test_http_tracer_reads_api_key_from_env_var(monkeypatch):
    monkeypatch.setenv("MINI_LANGFUSE_API_KEY", "key-from-env")
    fake = FakeClient()

    tracer =HTTPTracer(url="http://example.com/traces", client=fake)
    tracer.capture({"name": "foo"})
    assert fake.calls[0]["headers"] == {"Authorization": "Bearer key-from-env"}