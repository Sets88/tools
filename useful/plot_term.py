import argparse
from datetime import datetime
import sys

import plotext as plt


# # cat 1.csv
# 01/May/2024:03:43:21 +0000,0.002
# 01/May/2024:03:43:22 +0000,0.002
# 01/May/2024:03:43:23 +0000,0.003
# 01/May/2024:03:43:24 +0000,0.003
# 01/May/2024:03:43:25 +0000,0.002
# 01/May/2024:03:43:26 +0000,0.003
# # pip install plotext
# # cat 1.csv | plot_term.py

DATA_FORMAT = 'd/b/Y:H:M:S z'


def data_yield(args: argparse.Namespace) -> str:
    if args.file:
        for file in args.file:
            for line in open(file, 'r'):
                yield line

    if sys.stdin.isatty():
        return

    for line in sys.stdin:
        yield line


def parse_params() -> argparse.Namespace:
    """Parse command line parameters."""
    parser = argparse.ArgumentParser(description='Make plot of passed data')
    parser.add_argument('file', type=str, help='File to read', nargs='*')
    return parser.parse_args()


def main(args):
    plt.date_form(DATA_FORMAT)

    dates = []
    vals = []
    for line in data_yield(args):
        dt, val = line = line.strip().split(',')
        val = line[1]
        dates.append(dt)
        vals.append(float(val))

    plt.plot(dates, vals)
    plt.interactive()
    plt.yfrequency(50)
    plt.title("Some title")
    plt.xlabel("datetime")
    plt.ylabel("request time")
    plt.show()


if __name__ == '__main__':
    args = parse_params()
    main(args)
