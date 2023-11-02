import random
import asyncio
import weakref
import ssl


async def data_producer(queues: weakref.WeakSet[asyncio.Queue]):
    while True:
        data = str(random.randint(1, 100)) + '\n'

        for queue in queues:
            try:
                queue.put_nowait(data)
            except asyncio.QueueFull:
                queue.get_nowait()
                queue.put_nowait(data)

        await asyncio.sleep(1)


class Server:
    def __init__(self):
        self.queues = weakref.WeakSet()

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.streams.StreamWriter):
        queue = asyncio.Queue(10)

        self.queues.add(queue)

        try:
            while True:
                await reader.read(0)
                data = await queue.get()
                writer.write(data.encode())
        except Exception as exc:
            print(exc)
            del queue
            writer.close()

    async def run(self):
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile='path/to/certfile', keyfile='path/to/keyfile')

        # remove ssl param to disable ssl
        server = await asyncio.start_server(
            self.handle_connection,
            '0.0.0.0',
            8888,
            ssl=ssl_context
        )

        async with server:
            await server.serve_forever()


async def main():
    server = Server()
    await asyncio.gather(
        server.run(),
        data_producer(server.queues)
    )


if __name__ == '__main__':
    asyncio.run(main())
