#!/usr/bin/env python
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
rename_entries = {   
    "id": "entry_id",
}


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
        os.mkdir('logs')
    pd.DataFrame(data_entries).to_csv(f"logs/{string_date}.csv", index=False)


def get_entries(api_url, put_heads, 
            start_date=None, end_date=None, project_id=None, 
            task_id=None, user_id=None, billed=None, billable=None):
    
    entries_str = {
        "start_date": (f"start_date='{start_date}'" if start_date!=None else ""), 
        "end_date":   (f"end_date='{end_date}'"     if end_date!=None   else ""), 
        "project_id": (f"project_id={project_id}"   if project_id!=None else ""), 
        "task_id":    (f"task_id={task_id}"         if task_id!=None    else ""), 
        "user_id":    (f"user_id={user_id}"         if user_id!=None    else ""), 
        "billed":     (f"billed={billed}"           if billed!=None     else ""), 
        "billable":   (f"billable={billable}"       if billable!=None   else ""),
    }
    entries_str = {key: value for key, value in entries_str.items() if value!=''}
    
    if len(entries_str.values()):
        params = '?' + '&'.join(entries_str.values())
    
    url = f"{api_url}entries.json" + params

    response_entries = requests.get(url, headers=put_heads)
    entries = response_entries.json()
    
    entries_df = pd.DataFrame.from_dict(entries).rename(
        columns=rename_entries
    )
    
    columns = [
        "entry_id",
        "date",
        "hours",
        "notes",
        "locked",
        "created_at",
        "updated_at",
        "task_id",
        "user_id",
    ]
    
    return entries_df[columns]


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