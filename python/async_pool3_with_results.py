from random import random
import asyncio


async def get_number(sem: asyncio.Semaphore, i: int) -> int:
    async with sem:
        await asyncio.sleep(1 + random())
        return i


def print_number(tasks: set, future: asyncio.Future) -> None:
    try:
        print(future.result())
    finally:
        tasks.discard(future)


async def main():
    sem = asyncio.Semaphore(10)

    tasks = set()

    for i in range(100):
        async with sem:
            task = asyncio.create_task(get_number(sem, i))
            task.add_done_callback(lambda f: print_number(tasks, f))
            tasks.add(task)
            await asyncio.sleep(0)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
