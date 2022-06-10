import logging
import asyncio


async def atask(i):
    await asyncio.sleep(1)
    print (i)


class AsyncPool:
    def __init__(self, size, timeout=None):
        self.size = size
        self.timeout = timeout
        self._queue = asyncio.Queue(self.size)

    async def __aenter__(self):
        self._workers = [asyncio.create_task(self._loop()) for _ in range(self.size)]
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for i in range(self.size):
            await self._queue.put((None, None, None))

        await asyncio.gather(*self._workers)

    async def _loop(self):
        while True:
            try:
                func, args, kwargs = await self._queue.get()

                if func is None:
                    break
                await asyncio.wait_for(func(*args, **kwargs), self.timeout)
            except asyncio.exceptions.TimeoutError:
                # Timeout error handle here
                pass

            except Exception as exc:
                logging.exception('')


    async def push(self, func, *args, **kwargs):
        await self._queue.put((func, args, kwargs))


async def run():
    async with AsyncPool(10, timeout=2) as pool:
        for i in range(50):
            await pool.push(atask, i)


if __name__ == '__main__':
    asyncio.run(run())
