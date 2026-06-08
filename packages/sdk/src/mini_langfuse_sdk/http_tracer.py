import httpx
import os

class HTTPTracer:
    def __init__(self, url=None, client=None):
        self.url = url or os.environ.get("MINI_LANGFUSE_URL")
        self.client = client or httpx.Client()

    def capture(self, record):
        if self.url is None:
            return
        self.client.post(self.url, json=record)