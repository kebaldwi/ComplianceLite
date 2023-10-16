#!/usr/bin/env python3

####################################################################################
# project: DNAC-ComplianceMon
# module: service_scheduler.py
# author: kebaldwi@cisco.com
# use case: Simple Check of XML audit files against configuration
# developers:
#            Gabi Zapodeanu, TME, Enterprise Networks, Cisco Systems
#            Keith Baldwin, TSA, EN Architectures, Cisco Systems
#            Bryn Pounds, PSA, WW Architectures, Cisco Systems
####################################################################################

# This section builds maintains and schedules compliance audits.

#     ------------------------------- IMPORTS -------------------------------

import json
import os
import sched
import time

scheduler = sched.scheduler(time.time, time.sleep)
settings = {}

#     ----------------------------- DEFINITIONS -----------------------------

# Define function to run the scheduled program
def run_program(schedule_name):
    # Replace this with the code you want to run
    print(f"{schedule_name} is running...")

# Define function to schedule the program to run now
def schedule_now(schedule_name):
    # Schedule the program
    scheduler.enter(0, 1, run_program, argument=(schedule_name,))
    
    # Save the scheduled entry to settings
    settings["schedules"][schedule_name] = {"type": "now", "params": {}}
    
    # Save settings to file
    with open(settings_file, "w") as f:
        json.dump(settings, f)
    
    print(f"{schedule_name} scheduled to run now.")

# Define function to schedule the program to run one time at a scheduled time
def schedule_one_time(schedule_name):
    # Get user input for scheduling parameters
    date_str = input("Enter date (YYYY-MM-DD): ")
    time_str = input("Enter time (HH:MM:SS): ")
    
    # Convert input to timestamp
    timestamp = time.mktime(time.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M:%S"))
    
    # Schedule the program
    scheduler.enterabs(timestamp, 1, run_program, argument=(schedule_name,))
    
    # Save the scheduled entry to settings
    settings["schedules"][schedule_name] = {"type": "one_time", "params": {"timestamp": timestamp}}
    
    # Save settings to file
    with open(settings_file, "w") as f:
        json.dump(settings, f)
    
    print(f"{schedule_name} scheduled to run one time at {date_str} {time_str}.")

# Define function to schedule the program to run recurring at a specific interval of mins sec or hrs
def schedule_recurring_interval(schedule_name):
    # Get user input for scheduling parameters
    interval_str = input("Enter interval in seconds (0 for one-time only): ")
    
    # Convert input to interval
    interval = int(interval_str)
    
    # Schedule the program
    scheduler.enter(0, 1, run_program, argument=(schedule_name,))
    
    # Save the scheduled entry to settings
    settings["schedules"][schedule_name] = {"type": "recurring_interval", "params": {"interval": interval}}
    
    # Save settings to file
    with open(settings_file, "w") as f:
        json.dump(settings, f)
    
    if interval == 0:
        print(f"{schedule_name} scheduled to run one time.")
    else:
        print(f"{schedule_name} scheduled to run every {interval} seconds.")

# Define function to schedule the program to run recurring at a specific time of day starting at a certain date
def schedule_recurring_daily(schedule_name):
    # Get user input for scheduling parameters
    start_date_str = input("Enter start date (YYYY-MM-DD): ")
    start_time_str = input("Enter start time (HH:MM:SS): ")
    interval_str = input("Enter interval in days: ")
    
    # Convert input to timestamp and interval
    start_timestamp = time.mktime(time.strptime(start_date_str + " " + start_time_str, "%Y-%m-%d %H:%M:%S"))
    interval = int(interval_str) * 24 * 60 * 60
    
    # Schedule the program
    scheduler.enterabs(start_timestamp, 1, run_program, argument=(schedule_name,))
    
    # Save the scheduled entry to settings
    settings["schedules"][schedule_name] = {"type": "recurring_daily", "params": {"start_timestamp": start_timestamp, "interval": interval}}
    
    # Save settings to file
    with open(settings_file, "w") as f:
        json.dump(settings, f)
    
    print(f"{schedule_name} scheduled to run every {interval_str} days starting at {start_date_str} {start_time_str}.")

# Define function to schedule the program to run recurring at a specific day of the week at a certain time
def schedule_recurring_weekly(schedule_name):
    # Get user input for scheduling parameters
    day_of_week_str = input("Enter day of week (0-6 where Monday is 0): ")
    time_str = input("Enter time (HH:MM:SS): ")
    
    # Convert input to timestamp and day of week
    day_of_week = int(day_of_week_str)
    timestamp = time.mktime(time.strptime(time_str, "%H:%M:%S"))
    
    # Schedule the program
    now = time.time()
    scheduled = False
    while not scheduled:
        next_timestamp = timestamp + (day_of_week - time.localtime(now).tm_wday) * 24 * 60 * 60

        if next_timestamp < now:
            next_timestamp += 7 * 24 * 60 * 60

        scheduler.enterabs(next_timestamp, 1, run_program, argument=(schedule_name,))
        now = next_timestamp
        
        # Save the scheduled entry to settings
        settings["schedules"][schedule_name] = {"type": "recurring_weekly", "params": {"day_of_week": day_of_week, "timestamp": timestamp}}
        
        # Save settings to file
        with open(settings_file, "w") as f:
            json.dump(settings, f)
        
        print(f"{schedule_name} scheduled to run every week on {time.strftime('%A', time.strptime(str(day_of_week), '%w'))} at {time_str}.")
        
        scheduled = True

# Define function to schedule the program to run recurring at a specific day of the month at a certain time
def schedule_recurring_monthly(schedule_name):
    # Get user input for scheduling parameters
    day_of_month_str = input("Enter day of month (1-31): ")
    time_str = input("Enter time (HH:MM:SS): ")
    
    # Convert input to timestamp and day of month
    day_of_month = int(day_of_month_str)
    timestamp = time.mktime(time.strptime(time_str, "%H:%M:%S"))
    
    # Schedule the program
    now = time.time()
    scheduled = False
    while not scheduled:
        year = time.localtime(now).tm_year
        month = time.localtime(now).tm_mon
        
        if day_of_month > time.localtime(now).tm_mday:
            next_timestamp = time.mktime((year, month, day_of_month, *time.strptime(time_str, "%H:%M:%S")[3:6], 0, 0, -1))
        else:
            month += 1
            if month > 12:
                year += 1
                month = 1
            next_timestamp = time.mktime((year, month, day_of_month, *time.strptime(time_str, "%H:%M:%S")[3:6], 0, 0, -1))
        
        scheduler.enterabs(next_timestamp, 1, run_program, argument=(schedule_name,))
        now = next_timestamp
    
        # Save the scheduled entry to settings
        settings["schedules"][schedule_name] = {"type": "recurring_monthly", "params": {"day_of_month": day_of_month, "timestamp": timestamp}}
    
        # Save settings to file
        with open(settings_file, "w") as f:
            json.dump(settings, f)
    
        print(f"{schedule_name} scheduled to run every month on the {day_of_month_str}th at {time_str}.")

        scheduled = True

# Define function to remove a specific scheduled event
def remove_schedule(schedule_name):
	# Remove the scheduled event from scheduler and settings 
	if schedule_name in settings["schedules"]:
		for event in scheduler.queue:
			if event.argument == (schedule_name,):
				scheduler.cancel(event)
				break
				
		del settings["schedules"][schedule_name]
		
		with open(settings_file, "w") as f:
			json.dump(settings, f)
			
		print(f"{schedule_name} removed successfully.")
	else:
		print(f"{schedule_name} is not found.")

# Define function to edit a specific scheduled event 
def edit_schedule(schedule_name):
	# Edit the specific scheduled event 
	if schedule_name in settings["schedules"]:
		schedule_type = settings["schedules"][schedule_name]["type"]
		
		if schedule_type == "now":
			remove_schedule(schedule_name)
			schedule_now(schedule_name)
			
		elif schedule_type == "one_time":
			remove_schedule(schedule_name)
			schedule_one_time(schedule_name)
			
		elif schedule_type == "recurring_interval":
			remove_schedule(schedule_name)
			schedule_recurring_interval(schedule_name)
			
		elif schedule_type == "recurring_daily":
			remove_schedule(schedule_name)
			schedule_recurring_daily(schedule_name)
			
		elif schedule_type == "recurring_weekly":
			remove_schedule(schedule_name)
			schedule_recurring_weekly(schedule_name)
			
		elif schedule_type == "recurring_monthly":
			remove_schedule(schedule_name)
			schedule_recurring_monthly(schedule_name)
	else:
		print(f"{schedule_name} is not found.")

# Define function to delete a specific scheduled event 
def delete_schedule(schedule_name):
	# Delete the specific scheduled event 
	if schedule_name in settings["schedules"]:
		remove_schedule(schedule_name)
	else:
		print(f"{schedule_name} is not found.")

# Initialize scheduler
def menu_scheduler():
    scheduler = sched.scheduler(time.time, time.sleep)
    
    # Load settings from file
    settings_file = "settings.json"
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            settings = json.load(f)
    else:
        settings = {"schedules": {}}
    
    while True:
        print("\n\nSelect an option:")
        print("1. Schedule program to run now")
        print("2. Schedule program to run one time")
        print("3. Schedule program to run daily")
        print("4. Schedule program to run weekly")
        print("5. Schedule program to run monthly")
        print("6. Cancel a scheduled program")
        print("7. Exit")
        
        # Get user input for menu selection
        selection = input("\n\n> ")
        
        print("\n\n")
        # Handle menu selection
        if selection == "1":
            schedule_name = input("Enter a name for the schedule: ")
            schedule_now(schedule_name)
        elif selection == "2":
            schedule_name = input("Enter a name for the schedule: ")
            schedule_one_time(schedule_name)
        elif selection == "3":
            schedule_name = input("Enter a name for the schedule: ")
            schedule_recurring_daily(schedule_name)
        elif selection == "4":
            schedule_name = input("Enter a name for the schedule: ")
            schedule_recurring_weekly(schedule_name)
        elif selection == "5":
            schedule_name = input("Enter a name for the schedule: ")
            schedule_recurring_monthly(schedule_name)
        elif selection == "6":
            schedule_name = input("Enter the name of the schedule to cancel: ")
            delete_schedule(schedule_name)
        elif selection == "7":
            break
        else:
            print("Invalid selection. Please try again.")        

def main():
    scheduler = sched.scheduler(time.time, time.sleep)
    menu_scheduler()

#     ----------------------------- MAIN -----------------------------
# For testing and development purposes uncomment the code below

if __name__ == '__main__':
    scheduler = sched.scheduler(time.time, time.sleep)
    
    # Load settings from file
    settings_file = "settings.json"
    if os.path.exists(settings_file):
        with open(settings_file, "r") as f:
            settings = json.load(f)
    else:
        settings = {"schedules": {}}
    
    while True:
        print("Select an option:")
        print("1. Schedule program to run now")
        print("2. Schedule program to run one time")
        print("3. Schedule program to run daily")
        print("4. Schedule program to run weekly")
        print("5. Schedule program to run monthly")
        print("6. Cancel a scheduled program")
        print("7. Exit")
        
        # Get user input for menu selection
        selection = input("> ")
        
        # Handle menu selection
        if selection == "1":
            schedule_name = input("Enter a name for the schedule: ")
            schedule_now(schedule_name)
        elif selection == "2":
            schedule_name = input("Enter a name for the schedule: ")
            schedule_one_time(schedule_name)
        elif selection == "3":
            schedule_name = input("Enter a name for the schedule: ")
            schedule_recurring_daily(schedule_name)
        elif selection == "4":
            schedule_name = input("Enter a name for the schedule: ")
            schedule_recurring_weekly(schedule_name)
        elif selection == "5":
            schedule_name = input("Enter a name for the schedule: ")
            schedule_recurring_monthly(schedule_name)
        elif selection == "6":
            schedule_name = input("Enter the name of the schedule to cancel: ")
            delete_schedule(schedule_name)
        elif selection == "7":
            break
        else:
            print("Invalid selection. Please try again.")
