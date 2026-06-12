import httpx


class AsyncHTTPTracer:
    def __init__(self, url, api_key, client=None):
        self.url = url
        self.api_key = api_key
        self.client = client or httpx.Client()
        self._buffer = []

    def capture(self, record):
        self._buffer.append(record)

    async def flush(self):
        if not self._buffer:
            return
        self.client.post(
            self.url, 
            json=self._buffer,
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        self._buffer = []