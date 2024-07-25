import os
import struct
import argparse
import asyncio
import logging


CLIENT_READ_SIZE = 1000000
SERVER_READ_SIZE = 1000000


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('copy_file_client_server')


class Server:
    def __init__(self, config: argparse.Namespace):
        self.config = config

    def reader(self, filename, start, end):
        with open(filename, 'rb') as f:
            left = end - start
            f.seek(start)
            while True:
                if left <= 0:
                    break

                data = f.read(min(SERVER_READ_SIZE, left))
                left -= len(data)

                if not data:
                    break

                yield data

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.streams.StreamWriter):
        logger.info(f'Connection established with client {writer.get_extra_info("peername")}')
        try:
            file_size = os.path.getsize(self.config.file)
            writer.write(struct.pack('Q', file_size))
            start = struct.unpack('Q', await reader.read(8))[0]
            end = struct.unpack('Q', await reader.read(8))[0]

            logger.info(f'Client {writer.get_extra_info("peername")} from {start} to {end}')

            for data in self.reader(self.config.file, start, end):
                writer.write(data)
                await writer.drain()
            writer.close()

        except Exception as exc:
            print(exc)
            writer.close()

    async def run(self):
        logger.info(f'Starting server on {self.config.host}:{self.config.port}')

        server = await asyncio.start_server(
            self.handle_connection,
            self.config.host,
            self.config.port
        )

        async with server:
            await server.serve_forever()


class Client():
    def __init__(self, config: argparse.Namespace):
        self.config = config

    async def worker(self, start: int, end: int):
        reader, writer = await asyncio.open_connection(self.config.host, self.config.port)
        filename = self.config.file
        logger.info(f'Processing {start} - {end}')
        # Size
        await reader.read(8)

        writer.write(struct.pack('Q', start))
        writer.write(struct.pack('Q', end))

        fd = os.open(filename, os.O_WRONLY)
        os.lseek(fd, start, 0)

        while True:
            data = await reader.read(CLIENT_READ_SIZE)
            if not data:
                break
            os.write(fd, data)

    async def get_size(self):
        reader, writer = await asyncio.open_connection(self.config.host, self.config.port)
        size = struct.unpack('Q', await reader.read(8))[0]
        writer.close()
        return int(size)

    async def run(self):
        size = await self.get_size()
        workers = []
        if not os.path.exists(self.config.file):
            with open(self.config.file, 'wb') as f:
                f.seek(size - 1)
                f.write(b'\x00')

        logger.info(f'Full size: {size}')

        for i in range(self.config.workers):
            per_worker = size // ((self.config.workers - 1) or 1)
            start = i * per_worker
            end = (i + 1) * per_worker
            worker = asyncio.create_task(self.worker(start, end))
            workers.append(worker)

        await asyncio.gather(*workers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Download file using multiple tcp streams")
    parser.add_argument(
        '-s',
        '--server',
        help="Server mode which will serve file to clients, otherwise client mode is used",
        action='store_true',
        default=False
    )
    parser.add_argument(
        '-H',
        '--host',
        help='Host to listen on or connect to',
        type=str,
        default='0.0.0.0'
    )
    parser.add_argument(
        '-p',
        '--port',
        help='Port to listen on or connect to',
        type=int,
        default=8888
    )
    parser.add_argument(
        '-w',
        '--workers',
        help='Number of workers(tcp streams) to use, for clients only',
        type=int,
        default=5
    )
    parser.add_argument(
        'file',
        help='File to serve for server or save to for client',
        type=str
    )
    parsed = parser.parse_args()

    if parsed.server:
        server = Server(parsed)
        asyncio.run(server.run())
    else:
        client = Client(parsed)
        asyncio.run(client.run())
