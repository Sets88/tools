import asyncio


async def fn():
    await asyncio.sleep(2)
    return 'test'


def awaitc(coro):
    import threading

    result = {"result": None}

    def run_coro(result):
        loop = asyncio.new_event_loop()
        result['result'] = loop.run_until_complete(coro)

    t = threading.Thread(target=run_coro, args=(result,))
    t.start()
    t.join()
    return result['result']


print(awaitc(fn()))

# (Pdb) print(await fn())
# *** SyntaxError: 'await' outside function
# (Pdb++) print(awaitc(fn()))
# test
