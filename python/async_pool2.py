from typing import Union
import asyncio 


class AsyncPool:
    def __init__(self, size: int, timeout: Union[None, int, float] = None):
        self.semaphore = asyncio.Semaphore(size)
        self.timeout = timeout
        self.tasks = []
        self.cleanup_task = asyncio.create_task(self.cleanup())

    async def cleanup(self):
        while True:
            for task in list(self.tasks):
                if task.done():
                    self.tasks.remove(task)

            await asyncio.sleep(5)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        finally:
            self.cleanup_task.cancel()

    async def run_task(self, coro: asyncio.coroutine):
        try:
            await asyncio.wait_for(coro, self.timeout)
        finally:
            self.semaphore.release()

    async def push(self, coro: asyncio.coroutine):
        await self.semaphore.acquire()
        self.tasks.append(asyncio.create_task(self.run_task(coro)))


async def atask(i):
    await asyncio.sleep(1)
    print (i)


async def run():
    async with AsyncPool(10, timeout=2) as pool:
        for i in range(50):
            await pool.push(atask(i))


if __name__ == '__main__':
    asyncio.run(run())
