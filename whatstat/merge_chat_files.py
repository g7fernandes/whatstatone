#!/usr/bin/env python3

import argparse
from typing import TextIO, Tuple, List, Optional, Union
from reader import get_datetime
from datetime import datetime
import sys


def get_last_date(file: Union[TextIO, List[str]]) -> datetime:
    date = None
    if isinstance(file, List):
        for line in reversed(file):
            if date := get_datetime(line.split()):
                return date
    else:
        for line in reversed(list(file)):
            if date := get_datetime(line.split()):
                file.seek(0)
                return date
    raise SystemExit('File does not contain valid date.')


def get_first_date(str_list: List[str]) -> datetime:
    date = None
    for line in str_list:
        if date := get_datetime(line.split()):
            return date
    raise SystemExit('File does not contain valid date.')


def find_date_index(text_list: List, target: datetime) -> int:
    len_text_list = len(text_list)
    end = len_text_list
    start = 0
    date: Optional[datetime] = datetime(1970, 1, 1)
    line = -1
    while target != date:
        line = int((start + end) / 2) - 1
        date = None
        while not date:
            line += 1
            date = get_datetime(text_list[line].split())

            if line > end:
                return len_text_list
        dif = end - start
        if date > target:
            end = line
        elif date < target:
            start = line
        if end == 0:
            return 0
        if dif == end - start:
            sys.stdout.write('Warning: missing message at merge point.')
            return line
    return line


def join_chats(chats: List[Tuple[datetime, TextIO]]) -> List[str]:
    out = list(chats[0][1])
    for i in range(1, len(chats)):
        last_date = get_last_date(out)
        will_append = list(chats[i][1])
        line = find_date_index(will_append, chats[i - 1][0])
        out += will_append[line:]
        sys.stdout.write(f'Merged at date {last_date}\n')
    return out


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=('Merge two chats of the same conversation that cover'
                     'different times.')
    )

    parser.add_argument(
        'chat_files',
        nargs='+',
        help='Files of the same chat to merge',
    )

    parser.add_argument(
        '--output',
        '-o',
        help='Merged files name output.',
        default='merged.txt',
        type=str,
    )

    args = parser.parse_args()

    files = []

    for name in args.chat_files:
        f = open(name, 'r')
        files.append((get_last_date(f), f))

    files = sorted(files, key=lambda kv: kv[0])

    merged = open(args.output, 'w')
    for line in join_chats(files):
        merged.write(line)

    merged.close()
    for file in files:
        file[1].close()
