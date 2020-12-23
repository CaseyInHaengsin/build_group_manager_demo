import os
import csv
import json
from tempfile import NamedTemporaryFile
import shutil
from pathlib import Path
import requests
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv('TOKEN')
DOMAIN = os.getenv('DOMAIN')
GROUP_ID = os.getenv('GROUP_ID')
ROLE_ID = os.getenv('ROLE_ID')
CHECK_VAL = os.getenv('CHECK_VAL')
FILE_NAME = 'sample_data.csv'
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def main():
    current_group_members = get_group_users()
    csv_data = get_csv_data()
    if csv_data:
        go_through_data(csv_data, current_group_members)
    else:
        print("Nothing to do")


def go_through_data(csv_data, current_group_members):
    users_added = []
    for user in csv_data:
        user_id = get_and_compare_user(user[CHECK_VAL])
        if isinstance(user_id, dict):
            current_group_members.append(user_id['build_id'])
            users_added.append(user)
            
    status = update_group_roles(current_group_members)
    if status == 'success':
        update_csv(users_added)


def get_and_compare_user(val_to_compare):
    try:
        r = requests.get(f"{DOMAIN}/api/v1/users", params={CHECK_VAL: val_to_compare}, headers=HEADERS)
        if r.status_code == 200:
            returned_users = r.json()
            if len(returned_users) > 1:
                raise Exception(f"Too many users were found while checking: {CHECK_VAL} with the value: {val_to_compare}")
            if returned_users[0][CHECK_VAL] == val_to_compare:
                return {"build_id": returned_users[0]['id']}
            else:
                return None
        else:
            raise Exception('Failed to get user in get_and_compare_user function')
    except Exception as e:
        print(e)


def update_group_roles(vals):
    body = {"roles": [{
        "id": "members",
        "value": list(set(vals))
        }
    ]}
    try:
        r = requests.put(f"{DOMAIN}/api/v1/groups/{GROUP_ID}", headers=HEADERS, json=body)
        if r.status_code != 200:
            raise Exception(f"Failed to update group {GROUP_ID}")
        return 'success'
    except Exception as e:
        print(e)

def get_group_users():
    try:
        r = requests.get(f"{DOMAIN}/api/v1/groups/{GROUP_ID}?fields=roles", headers=HEADERS)
        if r.status_code == 200:
            for item in r.json()['roles']:
                if item['id'] == ROLE_ID:
                    return item['value']
        else:
            raise Exception('Failed to get users')
    except Exception as e:
        print(e)

def update_csv(users_to_update):
    csv_path = Path('.') / FILE_NAME
    tempfile = NamedTemporaryFile(mode='w', delete=False)
    with open(csv_path, 'r+') as csv_file, tempfile:
        reader = csv.DictReader(csv_file)
        writer = csv.DictWriter(tempfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            match = [user for user in users_to_update if user[CHECK_VAL] == row[CHECK_VAL]]
            if match:
                match[0].update(added_to_group='True')
                row = match[0]
            writer.writerow(row)
    shutil.move(tempfile.name, csv_path)
    

def get_csv_data():
    csv_data = []
    csv_path = Path('.') / FILE_NAME
    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row['added_to_group'] != 'True':
                csv_data.append(row)
            else:
                continue
    return csv_data

if __name__ == "__main__":
    main()