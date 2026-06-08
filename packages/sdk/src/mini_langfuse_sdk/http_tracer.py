import httpx
import os
import logging

logger = logging.getLogger(__name__)

class HTTPTracer:
    def __init__(self, url=None, api_key=None, client=None):
        self.url = url or os.environ.get("MINI_LANGFUSE_URL")
        self.api_key = api_key or os.environ.get("MINI_LANGFUSE_API_KEY")
        self.client = client or httpx.Client()
        if self.url is None:
            logger.warning("Mini-langfuse: URL not configured, traces will be discarded")

    def capture(self, record):
        if self.url is None:
            return
        headers = {"Authorization": f"Bearer {self.api_key}"}
        self.client.post(self.url, json=record, headers=headers)