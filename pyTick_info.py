#!/usr/bin/env python
"""pyTick, a CLI Tickspot API wrapper.

It is able to upload entries to Tickspot given the 
task_id and the amount of hours.

Dates in Tickspot use the format YYYY-mm-dd.

Usage: 
    pyTick_cli.py info [options]

options:
    --tasks                   Show tasks names and ids.
    --projects                Show projects names and ids.
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

    tickspot_data = calculate_tickspot(api_url, get_heads)
    
    if args['--tasks']:
        tasks_df = tickspot_tasks(tickspot_data)
        tasks_df.to_csv(path_or_buf=sys.stdout, index=False)
    elif args['--projects']:
        projects_df = tickspot_projects(api_url, get_heads)
        projects_df.to_csv(path_or_buf=sys.stdout, index=False)
    
    return


if __name__ == '__main__':
    main()
