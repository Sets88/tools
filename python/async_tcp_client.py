import asyncio
import socket
import ssl


async def client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        sock.connect(('127.0.0.1', 12312))

        # Or on no need to set socket opts just
        #reader, writer = await asyncio.open_connection('127.0.0.1', 12312, ssl=ssl_context)
        # remove ssl param to disable ssl
        reader, writer = await asyncio.open_connection(server_hostname='127.0.0.1', sock=sock, ssl=ssl_context)

        try:
            while True:
                try:
                    line = await asyncio.wait_for(reader.readline(), timeout=10)
                    print(line)
                    writer.write(b'test\n')
                except asyncio.TimeoutError:
                    print('Nothing received in 10 seconds')
        except:
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            raise


if __name__ == '__main__':
    asyncio.run(client())
