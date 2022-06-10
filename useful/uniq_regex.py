#! /usr/bin/env python3
from typing import Union
import sys
import re
import argparse


DATA = {}


def parse_params() -> argparse.Namespace:
    """Parse command line parameters."""
    parser = argparse.ArgumentParser(description='Find unique lines in a file.')
    parser.add_argument('file', type=str, help='File to read', nargs='*')
    parser.add_argument('-r', '--regex', type=str, help='Regex to match', required=True)
    parser.add_argument('-g', '--regex_groups', type=lambda arg: arg.split(','), help='Use group n from regex for key')
    parser.add_argument('-k', '--keys_only', action='store_true', help='Print keys only')
    parser.add_argument('-p', '--print_not_matched', action='store_true', help='Print not matched lines')
    parser.add_argument('-s', '--sort_by_key', action='store_true', help='Sort output by key')
    parser.add_argument('-n', '--sort_as_number', action='store_true', help='Sort output by key')
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


def try_coerce_to_int(value: str) -> Union[int, str]:
    try:
        return int(value)
    except ValueError:
        return value


def sorted_if_needed(args, data: dict) -> tuple[str, str]:
    if not args.sort_by_key:
        return data.items()

    if args.sort_as_number:
        return sorted(data.items(), key=lambda x: try_coerce_to_int(x[0]))

    return sorted(data.items(), key=lambda x: x[0])


def main(args: argparse.Namespace):
    lines_generator = data_yield(args)
    regex = re.compile(args.regex)

    for line in lines_generator:
        test = regex.search(line)

        if test:
            key = test.group()
            if args.regex_groups:
                key = []
                for reg_group in args.regex_groups:
                    key.append(test.groups()[int(reg_group)])
                key = tuple(key)

            DATA[key] = line[0:-1]
        elif args.print_not_matched:
            DATA[(line[0:-1],)] = line[0:-1]

    sorted_data = sorted_if_needed(args, DATA)

    if (args.keys_only):
        print("\n".join([" | ".join(y) for y in [x[0] for x in sorted_data]]))
        return

    print("\n".join([x[1] for x in sorted_data]))


if __name__ == '__main__':
    args = parse_params()
    main(args)
