import os
import asyncio
from typing import Union
from types import ModuleType

from playwright.async_api import async_playwright


class Public:
    @staticmethod
    async def is_item_available(page):
        button = await page.query_selector('app-product-action button')

        disabled_attr = await button.get_attribute('disabled')

        if disabled_attr is None:
            return True

        return False


# for Debug purpose
class SyncPool:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def push(self, task):
        await task


class AsyncPool:
    def __init__(self, size: int, timeout: Union[None, int, float] = None):
        self.semaphore = asyncio.Semaphore(size)
        self.timeout = timeout
        self.tasks = []
        self.cleanup_task = asyncio.create_task(self.cleanup())

    async def cleanup(self) -> None:
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

    async def run_task(self, coro: asyncio.coroutine) -> None:
        try:
            await asyncio.wait_for(coro, self.timeout)
        finally:
            self.semaphore.release()

    async def push(self, coro: asyncio.coroutine) -> None:
        await self.semaphore.acquire()
        self.tasks.append(asyncio.create_task(self.run_task(coro)))


def route(url: str) -> ModuleType:
    url = url.replace('https://www.', 'https://')

    if url.startswith('https://public.cy/'):
        return Public


def no_shop_found(url: str) -> None:
    print(f'No shop found for url {url}')


def item_available(url: str) -> None:
    print(f'Item is available on {url}')


def item_unavailable(url: str) -> None:
#    print(f'Item is unavailable on {url}')
    pass


def exception_occurred(exc: Exception, url: str) -> None:
    print(f'Exception {exc} occurred on {url}')


async def process_url(page, url: str) -> None:
    try:
        url = url.strip()
        #await page.wait_for_load_state('networkidle');

        shop = route(url)

        if not shop:
            no_shop_found(url)
            return

        await page.goto(url)

        if await shop.is_item_available(page):
            item_available(url)
        else:
            item_unavailable(url)
    except Exception as exc:
        exception_occurred(exc, url)
    finally:
        await page.close()


async def main() -> None:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True
        )
        urls_file = open(os.path.join(os.path.dirname(__file__), 'urls.txt'))

        async with AsyncPool(10, timeout=60) as pool:
#        async with SyncPool(10, timeout=20) as pool:

            while url := urls_file.readline():
                try:
                    page = await browser.new_page()
                    await pool.push(process_url(page, url))
                except Exception as exc:
                    exception_occurred(exc, url)

        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
