#!/usr/bin/env python
"""pyTick, A WIP CLI Tickspot API wrapper.

It is able to upload entries to Tickspot given the 
task_id and the amount of hours.

Usage:
    pyTick_cli.py csv [options] [-] [<filename> | <filenames>...] 

csv:
    filename  CSV file with the headers: 
              date, hours, notes, task_id.

options:
    -h --help     Show this screen.
    -v --verbose  Show also the cli arguments.
    --version     Show version."""
from dotenv import load_dotenv
from docopt import docopt
from pytick import *


def main():

    args = docopt(__doc__, version="pyTick 0.1")

    if args['--verbose']:
        print(args)

    # required to make requests, they contain credentials
    api_url, get_heads, put_heads = env_load()

    if args['-']:
        print(sys.stdin)
        csv(api_url, put_heads, sys.stdin)
    
    if args['<filenames>']:
        for input_stream in args['<filenames>']:
            csv(api_url, put_heads, input_stream)
    
    if args['<filename>']:
        csv(api_url, put_heads, args['<filename>'])
    return

if __name__ == '__main__':
    main()
