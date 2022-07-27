#!/usr/bin/env python
"""pyTick, A WIP CLI Tickspot API wrapper.

It is able to upload entries to Tickspot given the 
task_id and the amount of hours.

Usage:
    pyTick_cli.py entries (<start_date>) (<end_date>) [options] 

options:
    -p <project_id>, --project_id=<project_id>  Id of the project to filter by
    -t <task_id>, --task_id=<task_id>           Id of the task to filter by
    -u <user_id>, --user_id=<user_id>           Id of the user to filter by
    -b <billed>, --billed=<billed>              Filter entries by they billed 
                                                status (true or false)
    -B <billable>, --billable=<billable>        Filter entries by they billable 
                                                status (true or false)
    -r <target>, --report_daily=<target>        Produce a report of hours per 
                                                date per user, with remainder of 
                                                hours according to target_hours
                                                [default: 8].
    -h --help                                   Show this screen.
    -v --verbose                                Show also the cli arguments.
    --version                                   Show version."""
from dotenv import load_dotenv
from docopt import docopt
from pytick import *

def main():

    args = docopt(__doc__, version="pyTick 0.1")

    if args['--verbose']:
        print(args)

    # required to make requests, they contain credentials
    api_url, get_heads, put_heads = env_load()
    
    start_date  = args["<start_date>"]
    end_date    = args["<end_date>"]
    project_id  = args["--project_id"]
    task_id     = args["--task_id"]
    user_id     = args["--user_id"]
    billed      = args["--billed"]
    billable    = args["--billable"]
    conv = lambda x: (True if x=='true' else False if x=='false' else None)
    entries_kargs = {
        "start_date": (start_date), 
        "end_date":   (end_date), 
        "project_id": (project_id     if project_id != False else None), 
        "task_id":    (task_id        if task_id    != False else None), 
        "user_id":    (user_id        if user_id    != False else None), 
        "billed":     (conv(billed)   if billed     != False else None), 
        "billable":   (conv(billable) if billable   != False else None),
    }
    
    entries_df = get_entries(api_url, get_heads, **entries_kargs)
    if args['--report_daily']:
        cols = ['date', 'user_id']
        entries_df = entries_df.groupby(by=cols)[['hours']].sum().round(2)
        entries_df.loc[:,'remaining_hours'] = (
            float(args['--report_daily']) - entries_df.hours.values).round(2)
        num_cols = ['hours', 'remaining_hours']
        entries_df.to_csv(path_or_buf=sys.stdout)
        return
    entries_df.to_csv(path_or_buf=sys.stdout, index=False)
    return


if __name__ == '__main__':
    main()
