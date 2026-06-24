import asyncio
import logging
import os
from typing import Any, cast
import httpx
from mini_langfuse_sdk.http_tracer import HTTPClient

logger = logging.getLogger(__name__)


class AsyncHTTPTracer:
    client: HTTPClient

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        client: HTTPClient | None = None,
        batch_size: int = 50,
        flush_interval: float = 5.0,
    ) -> None:
        self.url = url or os.environ.get("MINI_LANGFUSE_URL")
        self.api_key = api_key or os.environ.get("MINI_LANGFUSE_API_KEY")
        self.client = client or cast(HTTPClient, httpx.Client())
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._worker_task: asyncio.Task[None] | None = None

        if self.url is None:
            logger.warning("Mini-Langfuse: URL not configured, traces will be discarded")
        if self.api_key is None:
            logger.warning("Mini-Langfuse: API key not configured, traces will be discarded")

    def capture(self, record: dict[str, Any]) -> None:
        if self.url is None or self.api_key is None:
            return
        self._queue.put_nowait(record)

    async def start(self) -> None:
        if self._worker_task is not None:
            return
        self._worker_task = asyncio.create_task(self._worker_loop())

    async def stop(self) -> None:
        if self._worker_task is None:
            return
        self._worker_task.cancel()
        try:
            await self._worker_task
        except asyncio.CancelledError:
            pass
        self._worker_task = None

    async def flush(self) -> None:
        if self.url is None or self.api_key is None:
            return
        batch = []
        while not self._queue.empty():
            batch.append(self._queue.get_nowait())
        if batch:
            await self._send_batch(batch)

    async def _worker_loop(self) -> None:
        batch = []
        while True:
            try:
                record = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=self.flush_interval,
                )
                batch.append(record)
                if len(batch) >= self.batch_size:
                    await self._send_batch(batch)
                    batch = []
            except asyncio.TimeoutError:
                if batch:
                    await self._send_batch(batch)
                    batch = []

    async def _send_batch(self, batch: list[dict[str, Any]]) -> None:
        if self.url is None or self.api_key is None:
            return
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

