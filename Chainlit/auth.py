import csv
from datetime import datetime, timedelta
import time
from session_manager import sessions
from ldap_auth import ldap_validate_user

def read_users():
    users = {}
    with open('users.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            users[row['username']] = {
                'counter': int(row['counter']) if row['counter'] else 0,
                'limit': int(row['limit']) if row['limit'] else 0
            }
    return users

def check_username(username):
    users = read_users()
    username_exists = username in users
    return username_exists

def validate_user(username, password):
    start_time = time.time()
    if check_username(username):
        validation_result = ldap_validate_user(username, password)
    else:
        validation_result = False
    end_time = time.time()
    print(f"validate_user took {end_time - start_time:.6f} seconds")
    return validation_result
