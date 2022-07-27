#!/usr/bin/env python
"""pyTick, A WIP CLI Tickspot API wrapper.

It is able to upload entries to Tickspot given the 
task_id and the amount of hours.

Usage: 
    pyTick_cli.py new <task_id> <hours> [options]

options:
    -n <date>, --note=<date>  A note on the task.
    -d <note>, --date=<note>  The date of the task in the format 
                              (YYYY-mm-dd) [default=today].                        
    -h --help                 Show this screen.
    -v --verbose              Show also the cli arguments.
    --version                 Show version."""
from dotenv import load_dotenv
from docopt import docopt
from pytick import *


def main():

    args = docopt(__doc__, version="pyTick 0.1")
    
    if args['--verbose']:
        print(args)

    # required to make requests, they contain credentials
    api_url, get_heads, put_heads = env_load()

    new(api_url, put_heads, args["--date"], args["<hours>"],
        args["--note"], args["<task_id>"])
    return


if __name__ == '__main__':
    main()
