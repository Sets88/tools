#!/usr/bin/env python3
# pip install scapy

import sys
import signal
import time
import argparse
from typing import Optional

import scapy.all as scapy


rtt_results = []


def parse_params() -> argparse.Namespace:
    """Parse command line parameters."""
    parser = argparse.ArgumentParser(description='Dump network traffic more extended traffic filter')
    parser.add_argument('-t', '--timeout', type=int, help='timeout', default=1)
    parser.add_argument('-s', '--payload-size', type=int, help='payload size', default=0)
    parser.add_argument('-c', '--count', type=int, help='port', default=1000)
    parser.add_argument('-p', '--port', type=int, help='port', default=443)
    parser.add_argument('host', type=str, help='')
    return parser.parse_args()


def send_syn_ping(target_ip_address: str, target_port: int, size_of_packet: int, timeout: int) -> Optional[scapy.IP]:
    ip = scapy.IP(dst=target_ip_address)
    tcp = scapy.TCP(sport=scapy.RandShort(), dport=target_port, flags="S")
    raw = scapy.Raw(b"X" * size_of_packet)
    packet = ip / tcp / raw
    resp = scapy.sr1(packet, timeout=timeout, verbose=0)
    return resp


def print_response(resp: Optional[scapy.IP], rtt: float):
    if resp:
        tcplayer = resp.getlayer(scapy.TCP)
        if tcplayer:
            print(f'len={resp.len} ip={resp.src} ttl={resp.ttl} {resp.flags} id={resp.id} sport={tcplayer.sport} '
                f'flags={tcplayer.flags} seq={tcplayer.seq} win={tcplayer.window} rtt={rtt} ms')
    else:
        print('No response')


def main(params: argparse.Namespace):
    for _ in range(params.count):
        start_ts = time.time()
        resp = send_syn_ping(params.host, params.port, params.payload_size, timeout=params.timeout)
        end_ts = time.time()
        rtt = round((end_ts - start_ts) * 1000, 3)

        print_response(resp, rtt)

        if resp:
            rtt_results.append(rtt)
        else:
            rtt_results.append(None)

        if (end_ts - start_ts) > params.timeout:
            continue

        time.sleep(abs(end_ts - start_ts - 1))

    print_results()


def print_results():
    successful_rtt_results = [rtt for rtt in rtt_results if rtt]
    packet_loss = round(100 - (len(successful_rtt_results) / len(rtt_results) * 100), 1)

    print('')
    print(f'--- {params.host} ping statistics ---')
    print(f'{len(rtt_results)} packets transmitted, {len(successful_rtt_results)} packets received, '
        f'{packet_loss}% packet loss')

    if successful_rtt_results:
        print(f'round-trip min/avg/max = {min(successful_rtt_results)}/'
            f'{round(sum(successful_rtt_results) / len(successful_rtt_results), 3)}/{max(successful_rtt_results)} ms')


def handler(_, __):
    print_results()
    sys.exit(0)


if __name__ == '__main__':
    params = parse_params()
    signal.signal(signal.SIGINT, handler)
    main(params)
