#!/usr/bin/env python3
# pip install scapy

import logging
import sys
import signal
import time
import argparse
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

logging.getLogger("scapy").setLevel(logging.ERROR)

import scapy.all as scapy


NTHREADS = 10
rtt_results = []


def parse_params() -> argparse.Namespace:
    """Parse command line parameters."""
    parser = argparse.ArgumentParser(description='Dump network traffic more extended traffic filter')
    parser.add_argument('-t', '--timeout', type=int, help='response timeout', default=1)
    parser.add_argument('-s', '--payload-size', type=int, help='payload size', default=0)
    parser.add_argument('-c', '--count', type=int, help='send this amount of packets', default=1000)
    parser.add_argument('-p', '--port', type=int, help='remot port', default=443)
    parser.add_argument('-l', '--loss-only', help='print loss percentage only', action='store_true')
    parser.add_argument('host', type=str, help='')
    return parser.parse_args()


def send_syn_ping(target_ip_address: str, target_port: int, size_of_packet: int, timeout: int):
    ip = scapy.IP(dst=target_ip_address)
    tcp = scapy.TCP(sport=scapy.RandShort(), dport=target_port, flags="S")
    raw = scapy.Raw(b"X" * size_of_packet)
    packet = ip / tcp / raw
    resp = scapy.sr1(packet, timeout=timeout, verbose=0)
    return resp


def print_response(resp: Optional[scapy.IP], rtt: float):
    if params.loss_only:
        return

    if resp:
        tcplayer = resp.getlayer(scapy.TCP)
        if tcplayer:
            print(f'len={resp.len} ip={resp.src} ttl={resp.ttl} {resp.flags} id={resp.id} sport={tcplayer.sport} flags={tcplayer.flags} seq={tcplayer.seq} win={tcplayer.window} rtt={rtt} ms')
    else:
        print('No response')


def run_task():
    start_ts = time.time()
    resp = send_syn_ping(params.host, params.port, params.payload_size, timeout=params.timeout)
    end_ts = time.time()
    rtt = round((end_ts - start_ts) * 1000, 3)

    print_response(resp, rtt)

    if resp:
        rtt_results.append(rtt)
    else:
        rtt_results.append(None)



def main():
    with ThreadPoolExecutor(max_workers=NTHREADS) as executor:
        for _ in range(params.count):
            executor.submit(run_task)

    print_results()


def print_results():
    if not rtt_results:
        if params.loss_only:
            return

        print('No results')
        sys.exit(1)

        return

    successful_rtt_results = [rtt for rtt in rtt_results if rtt]
    packet_loss = round(100 - (len(successful_rtt_results) / len(rtt_results) * 100), 1)

    if params.loss_only:
        print(f'{packet_loss}')
        return

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
    main()
