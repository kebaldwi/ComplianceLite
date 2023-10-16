#!/usr/bin/env python3

####################################################################################
# project: DNAC-ComplianceMon
# author: kebaldwi@cisco.com
# module: compliance_mon.py
# use case: Simple Check of XML audit files against configuration
# developers:
#            Gabi Zapodeanu, TME, Enterprise Networks, Cisco Systems
#            Keith Baldwin, TSA, EN Architectures, Cisco Systems
#            Bryn Pounds, PSA, WW Architectures, Cisco Systems
####################################################################################

# This program is written to meet the requirements set out in the README.md

#     ------------------------------- IMPORTS -------------------------------

import os
import sys
import os.path
import datetime
import pytz
import shutil

import difflib
import urllib3
import logging
import warnings
import re

import utils
import dnac_apis

from prime_compliance_dictionary import all_files_into_dict
from difference_engine import compliance_run
from service_email import *

from requests.auth import HTTPBasicAuth  # for Basic Auth
from urllib3.exceptions import InsecureRequestWarning  # for insecure https warnings

from configuration_template import DNAC_URL, DNAC_PASS, DNAC_USER, CONFIG_PATH, CONFIG_STORE, COMPLIANCE_STORE, DNAC_IP, DNAC_FQDN, JSON_STORE, REPORT_STORE, SMTP_FLAG, SYSTEM_STORE, APP_DIRECTORY

urllib3.disable_warnings(InsecureRequestWarning)  # disable insecure https warnings

DNAC_AUTH = HTTPBasicAuth(DNAC_USER, DNAC_PASS)

#     ----------------------------- DEFINITIONS -----------------------------

def os_setup():
    """Define OS settings for display"""
    if (os.name == 'posix'):
        os.system('clear')
    else:
        os.system('cls')
    if not sys.warnoptions:
        warnings.simplefilter("ignore")

def pause():
    """Define pause for keystroke to continue"""
    input("\nPress Enter to continue...\n") 
    if (os.name == 'posix'):
        os.system('clear')
    else:
        os.system('cls')

def data_library(CONFIG_PATH, CONFIG_STORE, REPORT_STORE, JSON_STORE, SYSTEM_STORE):
    Report_Files = os.path.join(CONFIG_PATH, REPORT_STORE)
    if not os.path.exists(Report_Files):
        os.makedirs(Report_Files)
    Json_Files = os.path.join(CONFIG_PATH, JSON_STORE)
    if not os.path.exists(Json_Files):
        os.makedirs(Json_Files)
    Config_Files = os.path.join(CONFIG_PATH, CONFIG_STORE)
    if not os.path.exists(Config_Files):
        os.makedirs(Config_Files)
    System_Files = os.path.join(CONFIG_PATH, SYSTEM_STORE)
    if not os.path.exists(System_Files):
        os.makedirs(System_Files)
        shutil.copy("/app/configuration_template.py","/app/DNAC-CompMon-Data/System/config-backup.py")
    else:
        shutil.copy("/app/DNAC-CompMon-Data/System/config-backup.py","/app/configuration_template.py")
    #os.chdir(Config_Files)
    return Config_Files, Report_Files, Json_Files

def compare_configs(cfg1, cfg2):
    """
    using unified diff function, compare two configs and identify the changes.
    '+' or '-' will be prepended in front of the lines with changes
    :param cfg1: old configuration file path and filename
    :param cfg2: new configuration file path and filename
    :return: text with config lines that changed
    """
    # open the old and new configuration files
    f1 = open(cfg1, 'r')
    old_cfg = f1.readlines()
    f1.close()
    f2 = open(cfg2, 'r')
    new_cfg = f2.readlines()
    f2.close()
    # compare the two specified config files {cfg1} and {cfg2}
    d = difflib.unified_diff(old_cfg, new_cfg, n=9)
    # create a diff_list that will include all the lines that changed
    # create a diff_output string that will collect the generator output from the unified_diff function
    diff_list = []
    diff_output = ''
    for line in d:
        diff_output += line
        if line.find('Current configuration') == -1:
            if line.find('Last configuration change') == -1:
                if (line.find('+++') == -1) and (line.find('---') == -1):
                    if (line.find('-!') == -1) and (line.find('+!') == -1):
                        if line.startswith('+'):
                            diff_list.append('\n' + line)
                        elif line.startswith('-'):
                            diff_list.append('\n' + line)
    # process the diff_output to select only the sections between '!' characters for the sections that changed,
    # replace the empty '+' or '-' lines with space
    diff_output = diff_output.replace('+!', '!')
    diff_output = diff_output.replace('-!', '!')
    diff_output_list = diff_output.split('!')
    all_changes = []
    for changes in diff_list:
        for config_changes in diff_output_list:
            if changes in config_changes:
                if config_changes not in all_changes:
                    all_changes.append(config_changes)
    # create a config_text string with all the sections that include changes
    config_text = ''
    for items in all_changes:
        config_text += items
    return config_text

def read_recent(DIRECTORY,filename):
    # Extract hostname from filename
    hostname = filename.split('_')[0]
    #Define filename pattern
    file_pattern = re.compile(f'{hostname}.*_run_config.txt')
    # get a list of all files in the directory that match the pattern
    files = [file for file in os.listdir(DIRECTORY) if file_pattern.search(file)]
    # Sort the files by modification time (most recent first)
    files.sort(key=os.path.getmtime, reverse=True)
    # read the most recent file
    if files:
        file = files[0]
        print(file)
        #file = os.path.join(DIRECTORY, files[0])
    else:
        file = ''
    return file

# uncomment the lines for development and testing if required.
def main():
    os_setup()
    AUDIT_DATABASE = {}
    COMPLIANCE_DIRECTORY = "IOSXE"
    COMP_CHECKS = os.path.join(APP_DIRECTORY, COMPLIANCE_STORE, COMPLIANCE_DIRECTORY)
    AUDIT_DATABASE = all_files_into_dict(COMP_CHECKS)
    #print(f"First the Audit Rules from Prime loaded for processing against configs\n\n",AUDIT_DATABASE)
    #pause()   
    Config_Files, Report_Files, Json_Files = data_library(APP_DIRECTORY,CONFIG_STORE,REPORT_STORE,JSON_STORE,SYSTEM_STORE)
    os.chdir(Config_Files)
    temp_run_config = "temp_run_config.txt"
    # logging, debug level, to file {application_run.log}
    logging.basicConfig(
        filename='../../DNAC-CompMon-Data/System/application_run.log',
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    #print("DNA Center Compliance Monitor:\n")
    #print("We are going to collect all configurations for routers and switches your DNA Center")
    #print("\n\nDNA CENTER INTEROGATED: " + DNAC_FQDN + " @ IP ADDRESS: " + DNAC_IP)
    #print("\n\nThis is the Token we will use for Authentication:")
    dnac_token = dnac_apis.get_dnac_jwt_token(DNAC_AUTH)
    #print('\nDNA Center AUTH Token: \n', dnac_token, '\n')
    #pause()   
    # get the DNA Center managed devices list (excluded wireless, for one location)
    all_devices_info = dnac_apis.get_all_device_info(dnac_token)
    all_devices_hostnames = []
    for device in all_devices_info:
        if device['family'] == 'Switches and Hubs' or device['family'] == 'Routers':
            all_devices_hostnames.append(device['hostname'])
    # Get the current date time in UTC timezone
    now_utc = datetime.datetime.now(pytz.UTC)
    # Convert to timezone
    time_zone = 'US/Eastern'
    tz = pytz.timezone(time_zone)
    now_tz = now_utc.astimezone(tz)
    # Format the date and time string
    date_str = now_tz.strftime('%m/%d/%Y').replace('/', '_')
    time_str = now_tz.strftime('%H:%M:%S').replace(':', '_')
    # get the config files, compare with existing (if one existing). Save new config if file not existing.
    for device in all_devices_hostnames:
        device_run_config = dnac_apis.get_device_config(device, dnac_token)
        filename = str(device) + '_' + date_str + '_run_config.txt'
        # save the running config to a temp file
        f_temp = open(temp_run_config, 'w')
        f_temp.write(device_run_config)
        f_temp.seek(0)  # reset the file pointer to 0
        f_temp.close()
        # check for existing configuration file
        # if yes; run the check for changes; diff function
        # if not; save; run the diff function
        # expected result create local config "database"
        # first get most recent config if exists
        recent_filename = read_recent(CONFIG_PATH,filename)
        if os.path.isfile(recent_filename):
            diff = compare_configs(recent_filename, temp_run_config)
            if diff != '':
                # retrieve the device location using DNA C REST APIs
                location = dnac_apis.get_device_location(device, dnac_token)
                # find the users that made configuration changes
                with open(temp_run_config, 'r') as f:
                    user_info = 'User info no available'
                    for line in f:
                        if 'Last configuration change' in line:
                            user_info = line
                # define the incident description and comment
                short_description = 'Configuration Change Alert - ' + device
                comment = 'The device with the name: ' + device + '\nhas detected a Configuration Change'
                #print(comment)
                # get the device health from DNA Center
                current_time_epoch = utils.get_epoch_current_time()
                device_details = dnac_apis.get_device_health(device, current_time_epoch, dnac_token)
                device_sn = device_details['serialNumber']
                device_mngmnt_ip_address = device_details['managementIpAddr']
                device_family = device_details['platformId']
                device_os_info = device_details['osType'] + ',  ' + device_details['softwareVersion']
                device_health = device_details['overallHealth']
                updated_comment = '\nDevice location: ' + location
                updated_comment += '\nDevice family: ' + device_family
                updated_comment += '\nDevice OS info: ' + device_os_info
                updated_comment += '\nDevice S/N: ' + device_sn
                updated_comment += '\nDevice Health: ' + str(device_health) + '/10'
                updated_comment += '\nDevice management IP address: ' + device_mngmnt_ip_address
                #print(updated_comment)
                updated_comment = '\nThe configuration changes are\n' + diff + '\n\n' + user_info
                #print(updated_comment)
                # new version discovered, save the running configuration to a file in the folder with the name
                f_config = open(filename, 'w')
                f_config.write(device_run_config)
                f_config.seek(0)
                f_config.close()
                # retrieve the device management IP address
                device_mngmnt_ip_address = dnac_apis.get_device_management_ip(device, dnac_token)
                DeviceConfig = "changed"
                #Device: New config version stored
            else:
                #Device: No configuration changes detected
                if filename != recent_filename:
                    # version saved, save the running configuration to a file in the folder with the name
                    f_config = open(filename, 'w')
                    f_config.write(device_run_config)
                    f_config.seek(0)
                    f_config.close()
                    # retrieve the device management IP address
                    device_mngmnt_ip_address = dnac_apis.get_device_management_ip(device, dnac_token)
                    #Device: config stored
                else:
                    DeviceConfig = "same"
                    #Device: config the same
        else:
            # new device discovered, save the running configuration to a file in the folder with the name
            # {Config_Files}
            f_config = open(filename, 'w')
            f_config.write(device_run_config)
            f_config.seek(0)
            f_config.close()
            # retrieve the device management IP address
            device_mngmnt_ip_address = dnac_apis.get_device_management_ip(device, dnac_token)
            DeviceConfig = "new"
            #Device: New device discovered
    #pause()
    Report_Files = REPORT_STORE
    Json_Files = JSON_STORE
    report = compliance_run("./", AUDIT_DATABASE, Report_Files, Json_Files)
    if SMTP_FLAG == "True":
        system_notification_app("../../DNAC-CompMon-Data/Reports/")
        outcome = "SUCCESS-EMAIL"
    else:
        outcome = "SUCCESS-NOEMAIL"
        #Unable to send Notification Email - as SMTP settings are not set
    return outcome

#     ----------------------------- MAIN -----------------------------
# uncomment the lines in definition main() for development and testing if required.

if __name__ == '__main__':
    main()
