import asyncio
import time


class RateLimitSender:
    """
    A rate-limiting sender that ensures messages are sent at most once per interval.
    """

    def __init__(self, send_fn, interval: float = 1.0):
        self._send_fn = send_fn
        self._interval = interval
        self._queue = asyncio.Queue()
        self._task = None

    async def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._sender_loop())

    async def stop(self):
        await self._queue.join()
        self._task.cancel()

    async def send(self, message: str):
        await self._queue.put(message)

    async def _sender_loop(self):
        last_sent = 0.0
        while True:
            msg = await self._queue.get()

            now = time.monotonic()
            elapsed = now - last_sent

            if elapsed < self._interval:
                await asyncio.sleep(self._interval - elapsed)

            await self._send_fn(msg)
            last_sent = time.monotonic()

            self._queue.task_done()
