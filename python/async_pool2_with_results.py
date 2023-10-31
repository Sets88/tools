import asyncio
from typing import Union
from functools import partial
from random import random


class Task:
    def __init__(self, task: asyncio.Task, future: asyncio.Future):
        self.task = task
        self.future = future

    async def get_result(self):
        if not self.future.done():
            await self.future

        return self.future.result()

    async def cancel(self):
        await self.future.cancel()
        await self.task.cancel()

    def __await__(self):
        return self.task


class AsyncPool:
    def __init__(self, size: int, timeout: Union[None, int, float] = None):
        self.semaphore = asyncio.Semaphore(size)
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def run_task(self, coro: asyncio.coroutine, future: asyncio.Future):
        try:
            result = await asyncio.wait_for(coro, self.timeout)
            future.set_result(result)
        except Exception as exc:
            future.set_exception(exc)
        finally:
            self.semaphore.release()

    async def push(self, coro: asyncio.coroutine):
        await self.semaphore.acquire()

        future = asyncio.Future()

        task = Task(
             asyncio.create_task(self.run_task(coro, future=future)),
             future
        )

        return task


async def atask(i):
    await asyncio.sleep(random() + 1.5)
    return i


def print_res(inp: int, future: asyncio.Future):
    try:
        output = future.result()
    except asyncio.TimeoutError:
        output = 'Timeout'

    print(inp, output)


async def await_and_print_result(inp: int, task: Task):
    try:
        output = await task.get_result()
    except asyncio.TimeoutError:
        output = 'Timeout'

    print(inp, output)


async def run():
    pool = AsyncPool(10, timeout=2)

    tasks = []

    for i in range(20):
        task = await pool.push(atask(i))

        # tasks.append(task)
        # task.future.add_done_callback(partial(print_res, i))

        tasks.append(asyncio.create_task(await_and_print_result(i, task)))

    await asyncio.wait(tasks)


if __name__ == '__main__':
    asyncio.run(run())
