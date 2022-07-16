#!/usr/bin/env python
"""pyTick, A WIP CLI Tickspot API wrapper.

It is able to upload entries to Tickspot given the 
task_id and the amount of hours.

Usage:
    pytick.py [options] --tasks
    pytick.py [options] --projects
    pytick.py [options] new (<task_id>) (<hours>) [entrie_args]
    pytick.py [options] csv [-] [<filename> | <filenames>...]
    pytick.py --version

entrie_args:
    -n --note=<string>  A note on the task.
    -d --date=<string>  The date of the task in the format 
                        (YYYY-mm-dd) [default=today].
new: 
    task_id  The id of the tasks you want to load, you can 
             find the one you are searching for by calling 
             pyTick with the --tasks.
    hours    A float with the amount of hours that the task 
             took to complete.

csv:
    filename  CSV file with the headers: 
              date, hours, notes, task_id.

options:
    -h --help     Show this screen.
    -v --verbose  Show also the cli arguments.
    --version     Show version."""
from dotenv import load_dotenv
from datetime import datetime
from docopt import docopt
from pathlib import Path
import pandas as pd
import requests
import json
import sys
import os

# renaming columns for joins
rename_projects = {
    'id': 'project_id',
    'name': 'project_name',
    'budget': 'project_budget',
    'date_closed': 'project_date_closed',
    'notifications': 'project_notifications',
    'billable': 'project_billable',
    'recurring': 'project_recurring',
    'client_id': 'client_id',
    'owner_id': 'owner_id',
    'url': 'project_url',
    'created_at': 'project_created_at',
    'updated_at': 'project_updated_at'
}
rename_tasks = {
    'id': 'task_id',
    'name': 'task_name',
    'budget': 'task_budget',
    'position': 'task_position',
    'project_id': 'project_id',
    'date_closed': 'task_date_closed',
    'billable': 'task_billable',
    'url': 'task_url',
    'created_at': 'task_created_at',
    'updated_at': 'task_updated_at'
}
rename_clients = {
    'id': 'client_id',
    'name': 'client_name',
    'archive': 'client_archive',
    'url': 'client_url',
    'updated_at': 'client_updated_at'
}


def main():

    args = docopt(__doc__, version="pyTick 0.1", options_first=True)

    if args['--verbose']:
        print(args)

    # required to make requests, they contain credentials
    api_url, get_heads, put_heads = env_load()

    if args['new']:
        new(api_url, put_heads, args["--date"], args["<hours>"],
            args["--note"], args["<task_id>"])
        return

    if args['csv']:
        if args['-']:
            print(sys.stdin)
            csv(api_url, put_heads, sys.stdin)
        
        if args['<filenames>']:
            for input_stream in args['<filenames>']:
                csv(api_url, put_heads, input_stream)
        
        if args['<filename>']:
            csv(api_url, put_heads, args['<filename>'])

    if args['--tasks']:
        tickspot_data = calculate_tickspot(api_url, get_heads)
        tasks_df = tickspot_tasks(tickspot_data)
        tasks_df.to_csv(path_or_buf=sys.stdout, index=False)
        return

    if args['--projects']:
        projects_df = tickspot_projects(api_url, get_heads)
        projects_df.to_csv(path_or_buf=sys.stdout, index=False)
        return


def env_load():

    # load credentials
    load_dotenv(dotenv_path=Path('.env'))

    creds = ((os.getenv('token') is not None)
             and (os.getenv('subscriptionID') is not None)
             and (os.getenv('userAgent') is not None))

    if not creds:
        aux_str = """
        Something is missing!
        
        Your .env does not have some of the fields in here:
            - token
            - subscriptionID
            - userAgent
        """
        print(aux_str)
        return

    # url
    api_url = f"https://www.tickspot.com/{os.getenv('subscriptionID')}/api/v2/"

    # user agent header, token and content type header for tickspot API
    user_agent = {"User-Agent": f"{os.getenv('userAgent')}"}
    get_heads = {
        "Authorization": f"Token token={os.getenv('token')}",
        **user_agent
    }
    put_heads = {"Content-Type": "application/json", **get_heads}

    return api_url, get_heads, put_heads


def new(api_url, put_heads, date, hours, notes, task_id):

    data = {
        "date": datetime.today().strftime('%Y-%m-%d'),
        "hours": hours,
        "notes": "",
        "task_id": task_id,
        "user_id": os.getenv('userID')
    }

    if date:
        data.update({"date": date})

    if notes:
        data.update({"notes": notes})

    response_post = requests.post(f"{api_url}entries.json",
                                  headers=put_heads,
                                  json=data)


def csv(api_url, put_heads, filename):

    headers = ["date", "hours", "notes", "task_id"]
    data_df = pd.read_csv(filepath_or_buffer=filename, 
                               usecols=headers,
                               header=0)
    data_entries = data_df.to_dict(orient='records')

    aux_list = []
    for index, data in enumerate(data_entries):
        response_post = requests.post(f"{api_url}entries.json",
                                      headers=put_heads,
                                      json=data)
        aux_list.append(response_post.json()['id'])

    for index, data in enumerate(data_entries):
        data['entry_id'] = aux_list[index]

    string_date = datetime.today().strftime('%Y-%m-%d_%H%M%S')
    if not os.path.isdir('logs'):
        os.makedir('logs')
    pd.DataFrame(data_entries).to_csv(f"logs/{string_date}.csv", index=False)


def calculate_tickspot(api_url, get_heads):

    # making requests
    response_projects = requests.get(f"{api_url}projects.json",
                                     headers=get_heads)
    response_tasks = requests.get(f"{api_url}tasks.json", headers=get_heads)
    response_clients = requests.get(f"{api_url}clients.json",
                                    headers=get_heads)

    # read data
    projects = response_projects.json()
    tasks = response_tasks.json()
    clients = response_clients.json()
    projects_df = pd.DataFrame.from_dict(projects).rename(
        columns=rename_projects)
    tasks_df = pd.DataFrame.from_dict(tasks).rename(columns=rename_tasks)
    clients_df = pd.DataFrame.from_dict(clients).rename(columns=rename_clients)

    # merge all into a master table
    tickspot_data = projects_df.merge(tasks_df,
                                      left_on='project_id',
                                      right_on='project_id').merge(
                                          clients_df,
                                          left_on='client_id',
                                          right_on='client_id')
    return tickspot_data


def tickspot_tasks(tickspot_data):

    tickspot_tasks = tickspot_data[[
        'task_id',
        'task_name',
        'project_name',
        'client_name',
    ]].drop_duplicates()

    return tickspot_tasks


def tickspot_projects(api_url, get_heads):
    response_projects = requests.get(f"{api_url}projects.json",
                                     headers=get_heads)
    projects = response_projects.json()
    projects_df = pd.DataFrame.from_dict(projects).rename(
        columns=rename_projects)

    tickspot_projects = projects_df[[
        'project_id',
        'project_name',
    ]].drop_duplicates()

    return tickspot_projects


if __name__ == '__main__':
    main()
