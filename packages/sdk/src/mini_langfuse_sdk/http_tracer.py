import httpx

class HTTPTracer:
    def __init__(self, url, client=None):
        self.url = url
        self.client = client or httpx.Client()

    def capture(self, record):
        self.client.post(self.url, json=record)