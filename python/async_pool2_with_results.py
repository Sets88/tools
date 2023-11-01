import asyncio
import weakref
from typing import Union
from functools import partial
from random import random


class Task:
    def __init__(self, task: asyncio.Task, future: asyncio.Future):
        self.await_result_task = None
        self.task = task
        self.future = future

    async def get_result(self):
        if not self.future.done():
            await self.future

        return self.future.result()

    async def await_result_async(self, callback, *args, **kwargs):
        await asyncio.wait([self.task])
        await callback(*args, task=self, **kwargs)

    def await_result_sync(self, callback, *args, **kwargs):
        # remove future to make both sync and async versions have same params
        new_args = args[0:-1]
        callback(*new_args, task=self, **kwargs)

    def cancel(self):
        self.task.cancel()
        self.future.cancel()

    def add_done_callback(self, callback, *args, **kwargs):
        if asyncio.iscoroutinefunction(callback):
            self.await_result_task = asyncio.create_task(
                self.await_result_async(callback, *args, **kwargs)
            )
            return

        self.future.add_done_callback(
            partial(self.await_result_sync, callback, *args, **kwargs)
        )

    def __await__(self):
        return self.task


class AsyncPool:
    def __init__(self, size: int, default_timeout: Union[None, int, float] = None):
        self.semaphore = asyncio.Semaphore(size)
        self.default_timeout = default_timeout
        self.tasks = weakref.WeakSet()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.wait(list(self.tasks))

    def __await__(self):
        return asyncio.wait(self.tasks).__await__()

    async def run_task(self, coro: asyncio.coroutine, future: asyncio.Future, timeout: Union[None, int, float] = None):
        if timeout is None:
            timeout = self.default_timeout

        try:
            result = await asyncio.wait_for(coro, timeout)
            future.set_result(result)
        except Exception as exc:
            future.set_exception(exc)

    async def push(self, coro: asyncio.coroutine, timeout: Union[None, int, float] = None):
        await self.semaphore.acquire()

        future = asyncio.Future()

        running_task = asyncio.create_task(
            self.run_task(coro, future=future, timeout=timeout)
        )

        running_task.add_done_callback(lambda _: self.semaphore.release() and coro.cr_running and coro.cr_running.close())

        self.tasks.add(running_task)

        task = Task(running_task, future)

        return task


async def atask(i):
    await asyncio.sleep(random() + 1.5)
    return i


def print_res(inp: int, task: Task):
    try:
        output = task.future.result()
    except asyncio.TimeoutError:
        output = 'Timeout'
    except asyncio.CancelledError:
        output = 'Cancelled'

    print(inp, output)


async def await_and_print_result(inp: int, task: Task):
    try:
        output = await task.get_result()
    except asyncio.TimeoutError:
        output = 'Timeout'
    except asyncio.CancelledError:
        output = 'Cancelled'

    print(inp, output)


async def run():
    pool = AsyncPool(10, default_timeout=2)
    tasks = []

    for i in range(20):
        task = await pool.push(atask(i))

        # Sync version
        # task.add_done_callback(print_res, i)
        # Async version
        task.add_done_callback(await_and_print_result, i)

        tasks.append(task)

    # Make sure all tasks are finished
    await pool


# Context manager version
async def run2():
    async with AsyncPool(10, default_timeout=2) as pool:
        tasks = []

        for i in range(20):
            task = await pool.push(atask(i))

            # Sync version
            # task.add_done_callback(print_res, i)
            # Async version
            task.add_done_callback(await_and_print_result, i)

            tasks.append(task)


if __name__ == '__main__':
    asyncio.run(run())
