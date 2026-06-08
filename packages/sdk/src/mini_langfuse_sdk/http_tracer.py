import httpx
import os
import logging

logger = logging.getLogger(__name__)

class HTTPTracer:
    def __init__(self, url=None, client=None):
        self.url = url or os.environ.get("MINI_LANGFUSE_URL")
        self.client = client or httpx.Client()
        if self.url is None:
            logger.warning("Mini-langfuse: URL not configured, traces will be discarded")

    def capture(self, record):
        if self.url is None:
            return
        self.client.post(self.url, json=record)