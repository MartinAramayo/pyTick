"""pyTick, A WIP CLI Tickspot API wrapper.

Usage:
    pytick.py --tasks 
    pytick.py --projects
    pytick.py new <task_id> <hours> [--note=<note>] [--date=<date>]
    pytick.py csv <filename>
    pytick.py (-h | --help)
    pytick.py --version

csv:
    filename    .csv file with the headers: date, hours,notes, task_id

Optional:
    --note=<string>   Note of entry.
    --date=<string>   Entry date.

Options:
    --tasks       Save task_id, task_name, project_name, client_name into 
                  tasks.csv and prints it
    --projects    Save project_id, project_name into projects.csv and prints it
    -h --help     Show this screen.
    --version     Show version.
"""
from dotenv import load_dotenv
from datetime import datetime
from docopt import docopt
from pathlib import Path
import pandas as pd
import requests
import json
import os


# Renaming columns for joins
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

    args = docopt(__doc__, version="pyTick 0.1")

    # required to make requests, they contain credentials
    api_url, get_heads, put_heads = env_load()

    if args['new']:
        new(api_url, put_heads, args["--date"], args["<hours>"],
            args["--note"], args["<task_id>"])
        return

    if args['csv']:
        csv(api_url, put_heads, args["<filename>"])
        return

    if args['--tasks']:
        tickspot_data = calculate_tickspot(api_url, get_heads)
        tasks_df = tickspot_tasks(tickspot_data)
        print(tasks_df.to_string(index=False))
        tasks_df.to_csv('tasks.csv', index=False)
        return

    if args['--projects']:
        projects_df = tickspot_projects(api_url, get_heads)
        print(projects_df.to_string(index=False))
        projects_df.to_csv('projects.csv', index=False)
        return


def env_load():

    # load credentials
    load_dotenv(dotenv_path=Path('../creds.env'))

    creds = ((os.getenv('subscriptionID') is not None)
             and (os.getenv('accessword') is not None)
             and (os.getenv('userAgent') is not None)
             and (os.getenv('userID') is not None)
             and (os.getenv('token') is not None)
             and (os.getenv('email') is not None))

    if not creds:
        print("Something is missing!")
        print()
        print("Your ../creds.env does not have some of the fields in here:")
        print("- subscriptionID")
        print("- accessword")
        print("- userAgent")
        print("- userID")
        print("- token")
        print("- email")
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

    data_entries = pd.read_csv(filename).to_dict(orient='records')

    aux = []
    for index, data in enumerate(data_entries):
        response_post = requests.post(f"{api_url}entries.json",
                                      headers=put_heads,
                                      json=data)
        aux.append(response_post.json()['id'])

    for index, data in enumerate(data_entries):
        data['entry_id'] = aux[index]

    string_date = datetime.today().strftime('%Y-%m-%d_%H%M%S')
    if not os.path.isdir('logs'):
        os.makedir('logs')
    pd.DataFrame(data_entries).to_csv(f"logs/{string_date}.csv", index=False)


def calculate_tickspot(api_url, get_heads):

    # making requests
    response_projects = requests.get(f"{api_url}projects.json",
                                     headers=get_heads)
    response_tasks = requests.get(f"{api_url}tasks.json", headers=get_heads)
    response_clients = requests.get(f"{api_url}clients.json", headers=get_heads)

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
                                          right_on='client_id'
                                      )
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
    # arguments
    main()
