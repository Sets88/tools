import asyncio
import socket


class DatagramProtocol:
    def __init__(self, recvq, sndq):
        self.recvq = recvq
        self.sndq = sndq
        self.transport = None

    async def writer(self):
        while True:
            msg = await self.sndq.get()
            self.transport.sendto(msg)

    async def send(self, msg):
        await self.sndq.put(msg)

    async def recv(self):
        return await self.recvq.get()

    def connection_made(self, transport):
        self.transport = transport

    def connection_lost(self, exc):
        pass

    def datagram_received(self, data, addr):
        self.recvq.put_nowait(data)

    def error_received(self, exc):
        print('Error received:', exc)



async def client():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        recvq = asyncio.Queue()
        sndq = asyncio.Queue()

        loop = asyncio.get_running_loop()

        await loop.sock_connect(sock, ('127.0.0.1', 12312))

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: DatagramProtocol(recvq=recvq, sndq=sndq),
            sock=sock
        )

        writer_task = asyncio.create_task(protocol.writer())

        try:
            while True:
                try:
                    await protocol.send(b'test')
                    data = await asyncio.wait_for(protocol.recv(), timeout=10)
                    print(data)
                except asyncio.TimeoutError:
                    print('Nothing received in 10 seconds')
        finally:
            transport.close()


if __name__ == '__main__':
    asyncio.run(client())
