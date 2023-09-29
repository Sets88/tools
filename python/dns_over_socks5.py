import struct
import socket

# pip install pysocks
import socks


PROXY_HOST = '127.0.0.1'
PROXY_PORT = 12312
PROXY_USER = ''
PROXY_PASS = ''

RESOLVE_HOST = 'google.com'
DNS_HOST = '8.8.8.8'


socks.set_default_proxy(
    socks.PROXY_TYPE_SOCKS5,
    addr=PROXY_HOST,
    port=PROXY_PORT,
    rdns=True,
    username=PROXY_USER,
    password=PROXY_PASS,
)

# Comment it to disable proxy
socket.socket = socks.socksocket


def get_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((DNS_HOST, 53))

    domain = b"".join([bytes([len(x)]) + x for x in RESOLVE_HOST.encode().split(b'.')])

    query_id = 1234  # Unique query ID
    flags = 0x0100  # Flags: 0x0100 - Recursion desired
    question_type = 0x0001  # Type AAA (IPv4)
    question_class = 0x0001  # Class IN (Internet)
    dns_query = struct.pack('!HHHHHH', query_id, flags, 1, 0, 0, 0) + \
        domain + struct.pack('!BHH', 0, question_type, question_class)

    sock.sendall(dns_query)

    response_data = sock.recv(1024)
    sock.close()
    (
        response_id,
        response_flags,
        response_questions,
        response_answers,
        response_authority,
        response_additional
    ) = struct.unpack('!HHHHHH', response_data[:12])

    return ".".join([str(x) for x in struct.unpack('BBBB', response_data[-4:])])


if __name__ == '__main__':
    print(get_ip())
