import httpx
import os
import logging
from typing import Any, Protocol

logger = logging.getLogger(__name__)

class HTTPClient(Protocol):
    def post(
        self,
        url: str,
        json: dict[str, Any] | list[dict[str, Any]],
        headers: dict[str, str] | None = None,
    ) -> Any: ...
class HTTPTracer:
    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        client: HTTPClient | None = None,
    ) -> None:
        self.url = url or os.environ.get("MINI_LANGFUSE_URL")
        self.api_key = api_key or os.environ.get("MINI_LANGFUSE_API_KEY")
        self.client = client or httpx.Client()
        if self.url is None:
            logger.warning("Mini-langfuse: URL not configured, traces will be discarded")
        if self.api_key is None:
            logger.warning("Mini-Langfuse: API key not configured, traces will be discarded")

    def capture(self, record):
        if self.url is None or self.api_key is None:
            return
        headers = {"Authorization": f"Bearer {self.api_key}"}
        self.client.post(self.url, json=record, headers=headers)