import asyncio


async def fn():
    await asyncio.sleep(2)
    return 'test'


def awaitc(coro, timeout=None):
    import threading

    result = {"result": None, "exception": None}

    def run_coro(result, timeout):
        loop = asyncio.new_event_loop()
        try:
            if timeout:
                result['result'] = loop.run_until_complete(asyncio.wait_for(coro, timeout))
            else:
                result['result'] = loop.run_until_complete(coro)
        except Exception as exc:
            result['exception'] = exc

    t = threading.Thread(target=run_coro, args=(result, timeout))
    t.start()
    t.join()

    if result['exception']:
        raise result['exception']

    return result['result']


print(awaitc(fn(), timeout=3))

# (Pdb) print(await fn())
# *** SyntaxError: 'await' outside function
# (Pdb++) print(awaitc(fn()))
# test
