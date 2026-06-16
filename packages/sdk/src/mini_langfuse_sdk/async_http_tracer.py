import asyncio
import logging
import httpx

logger = logging.getLogger(__name__)

class AsyncHTTPTracer:
    def __init__(self, url, api_key, client=None, batch_size=50):
        self.url = url
        self.api_key = api_key
        self.client = client or httpx.Client()
        self.batch_size = batch_size
        self._queue = asyncio.Queue()
        self._worker_task = None

    def capture(self, record):
        self._queue.put_nowait(record)

    async def start(self):
        if self._worker_task is not None:
            return
        self._worker_task = asyncio.create_task(self._worker_loop())

    async def stop(self):
        if self._worker_task is None:
            return
        self._worker_task.cancel()
        try:
            await self._worker_task
        except asyncio.CancelledError:
            pass
        self._worker_task = None

    async def flush(self):
        batch = []
        while not self._queue.empty():
            batch.append(self._queue.get_nowait())
        if batch:
            await self._send_batch(batch)

    async def _worker_loop(self):
        batch = []
        while True:
            record = await self._queue.get()
            batch.append(record)
            if len(batch) >= self.batch_size:
                await self._send_batch(batch)
                batch = []

    async def _send_batch(self, batch):
        try:
            self.client.post(
                self.url,
                json=batch,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
        except Exception:
            logger.warning(
                "Mini-Langfuse: failed to flush batch",
                exc_info=True,
            )