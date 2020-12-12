#!/usr/bin/env python3
import os
import json
from resolvers import reader
import argparse
import errno


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Whatsapp statistics creator from history files.'
    )

    parser.add_argument(
        'config_file',
        help='Settings file with information requested and customizations.',
        default='config.json',
        nargs='?',
        type=str
    )

    args = parser.parse_args()

    listener = 'y'
    while listener in 'yY':
        with open(args.config_file, 'r') as config_file:
            config = json.load(config_file)
        query = reader(config)

        try:
            os.mkdir(f'{config["folder_containing_history"]}_result')
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
            pass

        query.write_results(f'{config["folder_containing_history"]}_result')
        listener = input("Read query with config file again? [y/n]\n")
