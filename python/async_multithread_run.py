import asyncio
import time
import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor


NTHREADS = 10
#NPROCESSES = 4
N_ASYNC_CONCURRENT_TASK = 10


def task(n):
    time.sleep(random.random())
    print('sync', n)


async def awork(n):
    await asyncio.sleep(random.random())
    print('async', n)


async def atask(semaphore, n):
    async with semaphore:
        await awork(n)


async def run():
    loop = asyncio.get_running_loop()
    semaphore = asyncio.Semaphore(N_ASYNC_CONCURRENT_TASK)

#    with ProcessPoolExecutor(max_workers=NPROCESSES) as executor:
    with ThreadPoolExecutor(max_workers=NTHREADS) as executor:
        tasks = []

        for i in range(10000):
            if i % 2:
                tasks.append(loop.run_in_executor(executor, task, i))
            else:
                tasks.append(asyncio.create_task(atask(semaphore, i)))

        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(run())
