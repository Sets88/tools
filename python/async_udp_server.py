import asyncio


class DatagramProtocol:
    def __init__(self, recvq: asyncio.Queue, sndq: asyncio.Queue):
        self.recvq = recvq
        self.sndq = sndq
        self.transport = None

    async def writer(self):
        while True:
            addr, msg = await self.sndq.get()
            self.transport.sendto(msg, addr)

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data: bytes, addr: tuple[str, int]):
        self.recvq.put_nowait((addr, data))

    def error_received(self, exc):
        print('Error received:', exc)


class Connection:
    def __init__(self, addr: tuple[str, int], recvq: asyncio.Queue, sendq: asyncio.Queue) -> None:
        self.addr = addr
        self.recvq = recvq
        self.sendq = sendq

    async def send(self, msg: bytes):
        await self.sendq.put((self.addr, msg))

    async def recv(self, timeout=None, block=True) -> bytes:
        if timeout:
            return await asyncio.wait_for(
                self.recvq.get(),
                timeout
            )
        if not block:
            return self.recvq.get_nowait()

        return await self.recvq.get()


class Server:
    def __init__(self, handler) -> None:
        self.recvq = asyncio.Queue()
        self.sendq = asyncio.Queue()
        self.handler = handler
        self.handler_tasks = []
        self.connections = {}

    async def receive_msg(self):
        while True:
            addr, msg = await self.recvq.get()

            if addr not in self.connections:
                recvq = asyncio.Queue()
                self.connections[addr] = recvq

                self.handler_tasks.append(
                    asyncio.create_task(
                        self.handler(
                            Connection(addr, recvq, self.sendq)
                        )
                    )
                )

            recvq = self.connections[addr]
            recvq.put_nowait(msg)

    async def run(self):
        loop = asyncio.get_running_loop()

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: DatagramProtocol(recvq=self.recvq, sndq=self.sendq),
            local_addr=('0.0.0.0', 12312)
        )

        recv_task = asyncio.create_task(self.receive_msg())
        send_task = asyncio.create_task(protocol.writer())
        await asyncio.gather(recv_task, send_task)


async def connection_handler(connection: Connection):
    while True:
        data = await connection.recv()
        await connection.send(data)
        try:
            await connection.recv(block=False)
        except asyncio.QueueEmpty:
            pass
        await connection.send(b'!!!')


async def server():
    server = Server(connection_handler)
    await server.run()


if __name__ == '__main__':
    asyncio.run(server())
