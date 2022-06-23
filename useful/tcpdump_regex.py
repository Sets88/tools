#!/usr/bin/env python3
# pip install scapy

import argparse
import re
from datetime import datetime
from functools import partial
from typing import Union

from scapy.all import sniff
from scapy.layers.l2 import Ether


def parse_params() -> argparse.Namespace:
    """Parse command line parameters."""
    parser = argparse.ArgumentParser(description='Dump network traffic more extended traffic filter')
    parser.add_argument('-r', '--regex', type=str, help='Regex to match')
    parser.add_argument('-i', '--interface', type=str, help='interface', required=True)
    parser.add_argument('dump_filter', type=str, help='', nargs='*')
    return parser.parse_args()


def print_packet(packet: Ether):
    packet.show()


def process_packet(regex: Union[None, re.Pattern], packet: Ether):
    if regex:
        if regex.search(bytes(packet)):
            print_packet(packet)

        return

    print_packet(packet)


def main(params, regex: Union[None, re.Pattern]):
    dump_filter = None

    if params.dump_filter:
        dump_filter = " ".join(params.dump_filter)

    sniff(filter=dump_filter, prn=partial(process_packet, regex), iface=params.interface, store=False)


if __name__ == '__main__':
    regex = None
    params = parse_params()

    if params.regex:
        regex = re.compile(params.regex.encode('utf-8'))

    main(params, regex)
