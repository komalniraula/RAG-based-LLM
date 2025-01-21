import csv
import schedule
import time
import threading
from auth import read_users  # Import the read_users function from auth.py

# Function to write users to CSV
def write_users(users):
    with open('users.csv', mode='w') as file:
        writer = csv.DictWriter(file, fieldnames=['username', 'counter', 'limit'])
        writer.writeheader()
        for username, data in users.items():
            writer.writerow({'username': username, 'counter': data['counter'], 'limit': data['limit']})

# Function to reset counter daily at midnight
def reset_counter():
    users = read_users()
    for user in users.values():
        user['counter'] = 0
    write_users(users)

# Function to update the counter for a specific user
def update_counter(username):
    users = read_users()
    if username in users:
        users[username]['counter'] += 1
    write_users(users)

# Schedule the counter reset at midnight
schedule.every().day.at("00:00").do(reset_counter)

# Function to run scheduled tasks
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()
