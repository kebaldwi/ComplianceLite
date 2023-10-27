#!/usr/bin/env python3

####################################################################################
# project: DNAC-ComplianceMon
# module: compliance_summary.py
# author: kebaldwi@cisco.com
# use case: Simple Summary Report
# developers:
#            Gabi Zapodeanu, TME, Enterprise Networks, Cisco Systems
#            Keith Baldwin, TSA, EN Architectures, Cisco Systems
#            Bryn Pounds, PSA, WW Architectures, Cisco Systems
####################################################################################

# This program is written to ingest all the XML files exported from Prime and build
# A dictionary of auditing rules to be used to check configurations

#     ------------------------------- IMPORTS -------------------------------

import os
import re
import json
import datetime

#     ----------------------------- DEFINITIONS -----------------------------

# Get hostname and date from file name
def get_data_from_filename(filename):
    hostname, date_str = re.search(r'DCR-(.*?)-(\d{1,2}_\d{1,2}_\d{1,4})', filename).groups()
    date = datetime.datetime.strptime(date_str, '%m_%d_%Y')
    return hostname, date

# Get all recent versions of JSON files.
def get_recent_files(directory):
    # Get a list of all files in the directory
    files = os.listdir(directory)
    # Create a dictionary to store the most recent versions of each file
    recent_versions = {}
    # Iterate through the files
    for file in files:
        if file.endswith(".json"):
            device_name, file_date = get_data_from_filename(file)
            # Check if the file is already in the dictionary
            if device_name in recent_versions:
                existing_file_path, existing_file_date = recent_versions[device_name]
                # Compare the modification time with the current most recent version
                if file_date > existing_file_date:
                    file_path = os.path.join(directory, file)
                    recent_versions[device_name] = (file_path, file_date)
            else:
                # Add the file to the dictionary as the initial most recent version
                file_path = os.path.join(directory, file)
                recent_versions[device_name] = (file_path, file_date)
    # Create a list of filenames for all the most recent versions of files
    recent_files = [file_path for device_name, (file_path, _) in recent_versions.items()]
    return recent_files
