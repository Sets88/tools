import argparse
import sys
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates



def parse_params() -> argparse.Namespace:
    """Parse command line parameters."""
    parser = argparse.ArgumentParser(description='Make plot of passed data')
    # Example of file content
    # 1 2021-05-12T03:18
    # 1 2021-05-12T06:52
    # 2 2021-05-12T05:44
    # 3 2021-05-12T00:38
    #4 2021-05-12T07:43
    parser.add_argument('file', type=str, help='File to read', nargs='*')
    return parser.parse_args()


def data_yield(args: argparse.Namespace) -> str:
    if args.file:
        for file in args.file:
            for line in open(file, 'r'):
                yield line

    if sys.stdin.isatty():
        return

    for line in sys.stdin:
        yield line


def main(args):
    data = {}

    for line in data_yield(args):
        splited = line.split(' ')
        if len(splited) == 1 or not splited[0] or not splited[1]:
            continue
        val = int(splited[0].strip())
        dt = datetime.fromisoformat(splited[1].strip())
        data[dt] = val

    data = dict(sorted(data.items()))

    x = list(data.keys())
    y = list(data.values())

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d-%Y %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=100))
    plt.plot(x, y)
    plt.gcf().autofmt_xdate()
    plt.show()


if __name__ == '__main__':
    args = parse_params()
    main(args)
