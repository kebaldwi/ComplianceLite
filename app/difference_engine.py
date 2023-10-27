#!/usr/bin/env python3

####################################################################################
# project: DNAC-ComplianceMon
# module: difference_engine.py
# author: kebaldwi@cisco.com
# use case: Simple Check of XML audit files against configuration
# developers:
#            Gabi Zapodeanu, TME, Enterprise Networks, Cisco Systems
#            Keith Baldwin, TSA, EN Architectures, Cisco Systems
#            Bryn Pounds, PSA, WW Architectures, Cisco Systems
####################################################################################

# This program is written to ingest all the XML files exported from Prime and build
# A dictionary of auditing rules to be used to check configurations

#     ------------------------------- IMPORTS -------------------------------

import os
import sys
import os.path
import difflib
import json
import re
import datetime
import time
import pytz
from configuration_template import DNAC_IP, DNAC_FQDN, APP_DIRECTORY, COMPLIANCE_STORE
from prime_compliance_dictionary import all_files_into_dict
from report_module import pdf_converter, json_export
from showrunsection import show_run_section, show_run_section_array, show_run_headers

#     ----------------------------- DEFINITIONS -----------------------------

# This function pulls a rule from the dataset
def get_data_by_number(data, number):
    if number not in data:
        return None
    item = data[number]
    if isinstance(item, list):
        return item
    else:
        return [item]

# This function will compare rule against one config
def compare_rules(cfg, audit_item, i):
    """
    we will use the audit dictionary created to compare 
    against the configuration presented to determine if the
    configuration has violations
    :param cfg: configuration file path and filename
    :param audit_dict: imported dictionary of audit rules
    :return: text with config lines that violated in a dictionary
    """
    # open the old and new configuration fields
    f1 = open(cfg, 'r')
    cfg = f1.readlines()
    f1.close()
    # create a diff_list that will include all the lines that are non compliant
    violation_output = ''
    scope = audit_item['Scope']
    operator = audit_item['Operator']
    value = audit_item['Value']
    message = audit_item['Message']
    # for loop for a match in all_config
    if (scope == 'ALL_CONFIG') and ('MATCHES' in operator):
        for line in cfg:
            if value in line:
                violation_output = "test: "+str(i)+" -> "+message
    return violation_output

# This function will compare multiple rules against one config
def audit(cfg, data):
    """
    we will use the audit dictionary created to compare 
    against the configuration presented to determine if the
    configuration has violations
    :param cfg: configuration file path and filename
    :param audit_dict: imported dictionary of audit rules
    :return: text with config lines that violated in a dictionary
    """
    # open the old and new configuration fields
    f1 = open(cfg, 'r')
    cfg = f1.readlines()
    f1.close()
    # create a diff_list that will include all the lines that are non compliant
    violation_list = []
    violation_output = ''
    for i in range(0, (len(data)-1)):
        instance = []
        instance_output = []
        if isinstance(data[i], list):
            config_section = []
            output = False
            for sub_dict in data[i]:
                scope = (sub_dict['Scope'])
                operator = (sub_dict['Operator'])
                value = (sub_dict['Value'])
                if value.startswith("*"):
                    value = "." + value[1:]
                elif value.startswith("^*"):
                    value = "^." + value[2:]
                if "(.*)" in value:
                    value = value.replace('(.*)', '.*')
                message = (sub_dict['Message'])
                regex = re.compile(value)
                if scope == "SUBMODE_CONFIG":
                    config_section = show_run_section(cfg, regex)
                    config_subsections = show_run_section_array(config_section)
                    #print("\nTest: "+str(i)+"\nsection: ",config_section,"\nsubsection: ",config_subsections)
                    #print("\n\nsearch: ",regex)
                    if config_section != "":
                        output = True
                        carryonflag = True
                    else:
                        output = True
                        carryonflag = False
                    #print("\n\n",output,carryonflag)
                elif ((scope == "PREVIOUS_SUBMODE_CONFIG") and (len(config_section)!=0)):
                    for subsection in config_subsections:
                        #print(subsection)
                        if regex.search(subsection):
                            if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                                output = True
                                carryonflag == True
                                #print("1")
                            elif operator == "DOES_NOT_MATCH":
                                output = False
                                carryonflag = False
                                #print("2")
                                #print(regex.search(subsection))
                                #print(subsection)
                                instance.append(regex.search(subsection))
                                instance_output.append(subsection)
                        else:
                            if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                                output = False
                                carryonflag = False
                                #print("3")
                                #print(regex.search(subsection))
                                #print(subsection)
                                instance.append(regex.search(subsection))
                                instance_output.append(subsection)
                            elif operator == "DOES_NOT_MATCH":
                                output = True
                                carryonflag == True
                                #print("4")
                    #print(output,carryonflag)
            if output == True:
                violation_output = "test "+str(i)+": >> Passed"
            elif output == False:
                #violation_output = "test "+str(i)+": >> search: '"+value+"' >> Violation Msg: "+message
                violation_output = "test "+str(i)+": >> Violation Msg: "+message
                if (len(instance)>0):
                    violation_output = violation_output + "\n\nInstances:"
                    if (len(instance)>1):
                        for n in range(0,len(instance)-1):
                            if str(instance[n]) != "None":
                                #violation_output = violation_output + "\n" + str(instance[n])
                                violation_output = violation_output + "\n" + str(instance_output[n])
                    else:
                        if str(instance):
                            #violation_output = violation_output + "\n" + str(instance)
                            violation_output = violation_output + "\n" + str(instance_output[0])
                    violation_output = violation_output + "\n"
            violation_list.append(violation_output)
        if isinstance(data[i], dict):
            output = True
            scope = data[i]['Scope']
            operator = data[i]['Operator']
            value = data[i]['Value']
            if value.startswith("*"):
                value = "." + value[1:]
            elif value.startswith("^*"):
                value = "^." + value[2:]
            if "(.*)" in value:
                value = value.replace('(.*)', '.*')
            regex = re.compile(value)
            message = data[i]['Message']
            # for loop for a match in all_config
            for line in cfg:
                if regex.search(line):
                    if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                        output = True
                        break
                    else:
                        output = False
                elif value in line:
                    if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                        output = True
                        break
                    else:
                        output = False
                else:
                    if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                        output = False
                    else:
                        output = True
                        break                    
            if output == True:
                violation_output = "test "+str(i)+": >> Passed"
            elif output == False:
                #violation_output = "test "+str(i)+": >> search: '"+value+"' >> Violation Msg: "+message
                violation_output = "test "+str(i)+": >> Violation Msg: "+message
            violation_list.append(violation_output)
    return violation_list

# build a complaince report from the return data
def compliance_report(violation_list, filename):
    # Get the current date time in UTC timezone
    now_utc = datetime.datetime.now(pytz.UTC)
    
    # Convert to timezone
    time_zone = 'US/Eastern'
    est_tz = pytz.timezone(time_zone)
    now_est = now_utc.astimezone(est_tz)
    # Format the date and time string
    date_str = now_est.strftime('%m/%d/%Y')
    time_str = now_est.strftime('%H:%M:%S')
    # Create a list to stor the lines
    device = filename.split('_')[0]
    reportlines = []
    reportlines.append("\n\n ##################################################################################################")
    reportlines.append("         COMPLIANCE REPORT FROM " + date_str + " " + time_zone + " "+ time_str)
    reportlines.append("         DNA CENTER INTEROGATED: " + DNAC_FQDN + " @ IP ADDRESS: " + DNAC_IP)
    reportlines.append(" ##################################################################################################")
    reportlines.append("         DEVICE: " + device)
    reportlines.append(" ##################################################################################################\n")    
    for item in violation_list:
        reportlines.append(item)
    # Output to screen
    #print('\n'.join(reportlines))
    return reportlines

# Read one file
def xml_file_reader(file):
    # parse the  file
    with open(file, 'r') as f:
        open_file = f.read()
    return open_file

# Process multiple files
def compliance_run(directory, data, report_files, json_files):
    # Loop through each file in the directory
    report_path = "../../" + report_files
    json_path = "../../" + json_files
    compliance_data = []
    # Get the current date time in UTC timezone
    now_utc = datetime.datetime.now(pytz.UTC)
    # Convert to timezone
    time_zone = 'US/Eastern'
    tz = pytz.timezone(time_zone)
    now_tz = now_utc.astimezone(tz)
    # Format the date and time string
    date_str = now_tz.strftime('%m/%d/%Y').replace('/', '_')
    time_str = now_tz.strftime('%H:%M:%S').replace(':', '_')
    pdf_data = ""
    for filename in os.listdir(directory):
        if filename.endswith(date_str+'_run_config.txt') and "temp" not in filename:
            path = directory + filename
            violation_list = (audit(path, data))
            compliance_data = compliance_report(violation_list, filename)
            json_export(compliance_data, json_path)
            pdf_data = pdf_data + '\n'.join(compliance_data)
    pdf_filename = pdf_converter(pdf_data, report_path)
    return pdf_filename

# This function will compare multiple rules against one config passed to it in API
def external_audit(cfg, data):
    """
    we will use the audit dictionary created to compare 
    against the configuration presented to determine if the
    configuration has violations
    :param cfg: configuration file path and filename
    :param audit_dict: imported dictionary of audit rules
    :return: text with config lines that violated in a dictionary
    """
    # create a diff_list that will include all the lines that are non compliant
    violation_list = []
    violation_output = ''
    for i in range(0, (len(data)-1)):
        instance = []
        instance_output = []
        if isinstance(data[i], list):
            config_section = []
            output = False
            for sub_dict in data[i]:
                scope = (sub_dict['Scope'])
                operator = (sub_dict['Operator'])
                value = (sub_dict['Value'])
                if value.startswith("*"):
                    value = "." + value[1:]
                elif value.startswith("^*"):
                    value = "^." + value[2:]
                if "(.*)" in value:
                    value = value.replace('(.*)', '.*')
                message = (sub_dict['Message'])
                regex = re.compile(value)
                if scope == "SUBMODE_CONFIG":
                    config_section = show_run_section(cfg, regex)
                    config_subsections = show_run_section_array(config_section)
                    #print("\nTest: "+str(i)+"\nsection: ",config_section,"\nsubsection: ",config_subsections)
                    #print("\n\nsearch: ",regex)
                    if config_section != "":
                        output = True
                        carryonflag = True
                    else:
                        output = True
                        carryonflag = False
                    #print("\n\n",output,carryonflag)
                elif ((scope == "PREVIOUS_SUBMODE_CONFIG") and (len(config_section)!=0)):
                    for subsection in config_subsections:
                        #print(subsection)
                        if regex.search(subsection):
                            if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                                output = True
                                carryonflag == True
                                #print("1")
                            elif operator == "DOES_NOT_MATCH":
                                output = False
                                carryonflag = False
                                #print("2")
                                #print(regex.search(subsection))
                                #print(subsection)
                                instance.append(regex.search(subsection))
                                instance_output.append(subsection)
                        else:
                            if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                                output = False
                                carryonflag = False
                                #print("3")
                                #print(regex.search(subsection))
                                #print(subsection)
                                instance.append(regex.search(subsection))
                                instance_output.append(subsection)
                            elif operator == "DOES_NOT_MATCH":
                                output = True
                                carryonflag == True
                                #print("4")
                    #print(output,carryonflag)
            if output == True:
                violation_output = "test "+str(i)+": >> Passed"
            elif output == False:
                #violation_output = "test "+str(i)+": >> search: '"+value+"' >> Violation Msg: "+message
                violation_output = "test "+str(i)+": >> Violation Msg: "+message
                if (len(instance)>0):
                    violation_output = violation_output + "\n\nInstances:"
                    if (len(instance)>1):
                        for n in range(0,len(instance)-1):
                            if str(instance[n]) != "None":
                                #violation_output = violation_output + "\n" + str(instance[n])
                                violation_output = violation_output + "\n" + str(instance_output[n])
                    else:
                        if str(instance):
                            #violation_output = violation_output + "\n" + str(instance)
                            violation_output = violation_output + "\n" + str(instance_output[0])
                    violation_output = violation_output + "\n"
            violation_list.append(violation_output)
        if isinstance(data[i], dict):
            output = True
            scope = data[i]['Scope']
            operator = data[i]['Operator']
            value = data[i]['Value']
            if value.startswith("*"):
                value = "." + value[1:]
            elif value.startswith("^*"):
                value = "^." + value[2:]
            if "(.*)" in value:
                value = value.replace('(.*)', '.*')
            regex = re.compile(value)
            message = data[i]['Message']
            # for loop for a match in all_config
            for line in cfg:
                if regex.search(line):
                    if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                        output = True
                        break
                    else:
                        output = False
                elif value in line:
                    if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                        output = True
                        break
                    else:
                        output = False
                else:
                    if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                        output = False
                    else:
                        output = True
                        break                    
            if output == True:
                violation_output = "test "+str(i)+": >> Passed"
            elif output == False:
                #violation_output = "test "+str(i)+": >> search: '"+value+"' >> Violation Msg: "+message
                violation_output = "test "+str(i)+": >> Violation Msg: "+message
            violation_list.append(violation_output)
    return violation_list

# This function will compare multiple rules against one config passed to it in API
def external_audit_api(cfg):
    """
    we will use the audit dictionary created to compare 
    against the configuration presented to determine if the
    configuration has violations
    :param cfg: configuration file path and filename
    :param audit_dict: imported dictionary of audit rules
    :return: text with config lines that violated in a dictionary
    """
    # create a diff_list that will include all the lines that are non compliant
    violation_list = []
    violation_output = ''
    COMPLIANCE_DIRECTORY = "IOSXE"
    COMP_CHECKS = os.path.join(APP_DIRECTORY, COMPLIANCE_STORE, COMPLIANCE_DIRECTORY)
    data = all_files_into_dict(COMP_CHECKS)    
    for i in range(0, (len(data)-1)):
        instance = []
        instance_output = []
        if isinstance(data[i], list):
            config_section = []
            output = False
            for sub_dict in data[i]:
                scope = (sub_dict['Scope'])
                operator = (sub_dict['Operator'])
                value = (sub_dict['Value'])
                if value.startswith("*"):
                    value = "." + value[1:]
                elif value.startswith("^*"):
                    value = "^." + value[2:]
                if "(.*)" in value:
                    value = value.replace('(.*)', '.*')
                message = (sub_dict['Message'])
                regex = re.compile(value)
                if scope == "SUBMODE_CONFIG":
                    config_section = show_run_section(cfg, regex)
                    config_subsections = show_run_section_array(config_section)
                    #print("\nTest: "+str(i)+"\nsection: ",config_section,"\nsubsection: ",config_subsections)
                    #print("\n\nsearch: ",regex)
                    if config_section != "":
                        output = True
                        carryonflag = True
                    else:
                        output = True
                        carryonflag = False
                    #print("\n\n",output,carryonflag)
                elif ((scope == "PREVIOUS_SUBMODE_CONFIG") and (len(config_section)!=0)):
                    for subsection in config_subsections:
                        #print(subsection)
                        if regex.search(subsection):
                            if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                                output = True
                                carryonflag == True
                                #print("1")
                            elif operator == "DOES_NOT_MATCH":
                                output = False
                                carryonflag = False
                                #print("2")
                                #print(regex.search(subsection))
                                #print(subsection)
                                instance.append(regex.search(subsection))
                                instance_output.append(subsection)
                        else:
                            if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                                output = False
                                carryonflag = False
                                #print("3")
                                #print(regex.search(subsection))
                                #print(subsection)
                                instance.append(regex.search(subsection))
                                instance_output.append(subsection)
                            elif operator == "DOES_NOT_MATCH":
                                output = True
                                carryonflag == True
                                #print("4")
                    #print(output,carryonflag)
            if output == True:
                violation_output = "test "+str(i)+": >> Passed"
            elif output == False:
                #violation_output = "test "+str(i)+": >> search: '"+value+"' >> Violation Msg: "+message
                violation_output = "test "+str(i)+": >> Violation Msg: "+message
                if (len(instance)>0):
                    violation_output = violation_output + "\n\nInstances:"
                    if (len(instance)>1):
                        for n in range(0,len(instance)-1):
                            if str(instance[n]) != "None":
                                #violation_output = violation_output + "\n" + str(instance[n])
                                violation_output = violation_output + "\n" + str(instance_output[n])
                    else:
                        if str(instance):
                            #violation_output = violation_output + "\n" + str(instance)
                            violation_output = violation_output + "\n" + str(instance_output[0])
                    violation_output = violation_output + "\n"
            violation_list.append(violation_output)
        if isinstance(data[i], dict):
            output = True
            scope = data[i]['Scope']
            operator = data[i]['Operator']
            value = data[i]['Value']
            if value.startswith("*"):
                value = "." + value[1:]
            elif value.startswith("^*"):
                value = "^." + value[2:]
            if "(.*)" in value:
                value = value.replace('(.*)', '.*')
            regex = re.compile(value)
            message = data[i]['Message']
            # for loop for a match in all_config
            for line in cfg:
                if regex.search(line):
                    if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                        output = True
                        break
                    else:
                        output = False
                elif value in line:
                    if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                        output = True
                        break
                    else:
                        output = False
                else:
                    if operator == "MATCHES_EXPRESSION" or operator == "CONTAINS":
                        output = False
                    else:
                        output = True
                        break                    
            if output == True:
                violation_output = "test "+str(i)+": >> Passed"
            elif output == False:
                #violation_output = "test "+str(i)+": >> search: '"+value+"' >> Violation Msg: "+message
                violation_output = "test "+str(i)+": >> Violation Msg: "+message
            violation_list.append(violation_output)
    return violation_list

#     ----------------------------- MAIN -----------------------------
# code below should be uncommented for development purposes and testing only

"""
def main():
    data = {}
    dataset = {0: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'logging origin-id hostname', 'Message': 'MISSING logging origin-id hostname'}, 1: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'aaa authentication login default', 'Message': 'MISSING aaa authentication login default'}, 2: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'interface (.*)Ethernet(.*)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': '(no ip address|switchport|shutdown)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'ip address .*', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'DOES_NOT_MATCH', 'Value': 'ip address (10|127|167\\.24\\.4[0-7]\\.*|172\\.(?:1[6-9]|2[0-9]|3[01])|192\\.168\\..* 255.255..*)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'DOES_NOT_MATCH', 'Value': 'encapsulation dot1Q', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'ip access-group (INTERNET-INBOUND|USAAVPN) in', 'Message': 'MISSING ip access-group INTERNET-INBOUND on <1.1> <1.2>'}], 3: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'no snmp-server', 'Message': 'none'}, 4: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'Loopback', 'Message': 'Missing Loopback Interface'}, 5: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'aaa authentication login default', 'Message': 'MISSING aaa authentication login default'}, 6: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'service timestamps debug datetime', 'Message': 'MISSING service timestamps debug datetime'}, 7: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'logging host', 'Message': 'MISSING logging host IP address'}, 8: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'aaa authentication login default', 'Message': 'MISSING aaa authentication login default'}, 9: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'interface .*Ethernet.*', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': '(no ip address|switchport|shutdown)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'ip address .*', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'DOES_NOT_MATCH', 'Value': 'ip address (10|127|167\\.24\\..*|172\\.(?:1[6-9]|2[0-9]|3[01])|192\\.168\\..* 255.255..*)', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'ip access-list extended (INTERNET-INBOUND|USAAVPN)', 'Message': 'MISSING ip access-list extended INTERNET-INBOUND|USAAVPN'}], 10: {'Scope': 'ALL_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'snmp-server community private', 'Message': 'private for snmp-server community is set'}, 11: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip tacacs source-interface', 'Message': 'MISSING ip tacacs source-interface'}, 12: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ntp source Loopback', 'Message': 'MISSING ntp source Loopback'}, 13: {'Scope': 'ALL_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'snmp-server community public', 'Message': 'Unset public for snmp-server community'}, 14: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'aaa accounting commands 15', 'Message': 'MISSING aaa accounting commands 15'}, 15: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'logging trap informational', 'Message': 'none'}, 16: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'banner exec ^C', 'Message': 'MISSING banner exec'}, 17: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'no logging on', 'Message': 'MISSING logging on'}, 18: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'aaa authentication enable default', 'Message': 'MISSING aaa authentication enable default'}, 19: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'snmp-server host', 'Message': 'snmp-server host not enabled'}, 20: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip access-list standard SNMP_ACL_RO', 'Message': 'MISSING ip access-list standard SNMP_ACL_RO from config'}, 21: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'aaa authentication login default', 'Message': 'MISSING aaa authentication login default'}, 22: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'banner login ^C', 'Message': 'MISSING banner login'}, 23: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'logging buffered', 'Message': 'MISSING logging buffered'}, 24: {'Scope': 'DATASET', 'Operator': 'CONTAINS', 'Value': 'RW', 'Message': 'RW is set for snmp-server community'}, 25: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip tftp source-interface', 'Message': 'none'}, 26: {'Scope': 'DATASET', 'Operator': 'CONTAINS', 'Value': 'SNMP_ACL_RO', 'Message': 'snmp-server community does have SNMP_ACL_RO acl'}, 27: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'aaa new-model', 'Message': 'MISSING aaa new-model'}, 28: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'logging console critical', 'Message': 'none'}, 29: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'banner motd ^C', 'Message': 'MISSING banner motd'}, 30: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router eigrp (.*)', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip authentication key-chain eigrp', 'Message': 'MISSING ip authentication key-chain eigrp'}], 31: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'service password-encryption', 'Message': 'MISSING service password-encryption'}, 32: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'service tcp-keepalives-in', 'Message': 'MISSING service tcp-keepalives-in'}, 33: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip access-list extended SSH_ACCESS', 'Message': 'MISSING ip access-list extended SSH_ACCESS'}, 34: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'no interface tunnel', 'Message': 'none'}, 35: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'no ip proxy-arp', 'Message': 'MISSING no ip proxy-arp'}, 36: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'line vty (.*)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'CONTAINS', 'Value': 'access-class SSH_ACCESS in', 'Message': 'MISSING access-class SSH_ACCESS in on Line VTY <1.1>'}], 37: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'service tcp-keepalives-out', 'Message': 'MISSING service tcp-keepalives-out'}, 38: {'Scope': 'DATASET', 'Operator': 'CONTAINS', 'Value': 'secret', 'Message': 'MISSING Password Secret 5'}, 39: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router eigrp (.*)', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip authentication mode eigrp', 'Message': 'MISSING EIGRP ip authentication mode eigrp'}], 40: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'enable secret 5', 'Message': 'MISSING enable secret from config'}, 41: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip identd', 'Message': 'MISSING no ip identd'}, 42: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'line con(.*)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'CONTAINS', 'Value': 'session-timeout 10', 'Message': 'MISSING session-timeout 10 on Con 0'}], 43: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'no ip source-route', 'Message': 'no ip source-route'}, 44: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'line aux (.*)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'CONTAINS', 'Value': 'session-timeout 10', 'Message': 'MISSING session-timeout 10 on line aux 0'}], 45: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'no service dhcp', 'Message': 'none'}, 46: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'CONTAINS', 'Value': 'line vty (.*)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'CONTAINS', 'Value': 'transport input ssh', 'Message': 'line vty <1.1> is missing transport input ssh'}], 47: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip verify unicast source reachable-via', 'Message': 'none'}, 48: {'Scope': 'SUBMODE_CONFIG', 'Operator': 'CONTAINS', 'Value': 'no exec', 'Message': 'MISSING no exec on AUX 0'}, 49: [{'Scope': 'DEVICE_PROPERTIES', 'Operator': 'MATCHES_EXPRESSION', 'Value': '*C3560C.*|.*C2960.*', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'no ip bootp server', 'Message': 'MISSING no ip bootp server'}], 50: {'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'username .* privilege .* secret .*', 'Message': 'none'}, 51: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'no cdp run', 'Message': 'none'}, 52: {'Scope': 'SUBMODE_CONFIG', 'Operator': 'CONTAINS', 'Value': 'transport input none', 'Message': 'MISSING transport input none on line aux<1.1>'}, 53: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'CONTAINS', 'Value': 'router eigrp (.*)', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'key chain', 'Message': 'MISSING EIGRP Key Chain'}], 54: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router rip (.*)', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'key-string', 'Message': 'MISSING RIP key-string'}], 55: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router rip (.*)', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'key', 'Message': 'MISSING RIP key'}], 56: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router eigrp (.*)', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'key', 'Message': 'MISSING EIGRP key'}], 57: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router rip (.*)', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'key chain', 'Message': 'MISSING RIP key chain'}], 58: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router eigrp (.*)', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'key-string', 'Message': 'MISSING EIGRP Key-String'}], 59: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router eigrp (.*)', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'authentication mode md5', 'Message': 'MISSING authentication mode md5'}], 60: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router rip (.*)', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip rip authentication mode', 'Message': 'MISSING RIP ip rip authentication mode'}], 61: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'no service pad', 'Message': 'MISSING no service pad'}, 62: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router rip (.*)', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip rip authentication key-chain', 'Message': 'MISSING RIP ip rip authentication key-chain'}], 63: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router eigrp (.*)', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'authentication key-chain', 'Message': 'MISSING EIGRP authentication key-chain'}], 64: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router eigrp (.*)', 'Message': 'none'}, {'Scope': 'SUBMODE_CONFIG', 'Operator': 'CONTAINS', 'Value': 'address-family ipv4 autonomous-system', 'Message': 'MISSING EIGRP address-family ipv4 autonomous-system'}], 65: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip ssh version 2', 'Message': 'MISSING ip ssh version 2'}, 66: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'CONTAINS', 'Value': 'line tty (.*)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'CONTAINS', 'Value': 'session-timeout 10', 'Message': 'MISSING session-timeout 10 on YTY Lines'}], 67: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'line vty (.*)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'CONTAINS', 'Value': 'session-timeout 10', 'Message': 'MISSING session-timeout 10 on LINE VTY <1.1>'}], 68: {'Scope': 'DATASET', 'Operator': 'CONTAINS', 'Value': 'DES', 'Message': 'AES is not enabled on SNMPv3 user'}, 69: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router eigrp (.*)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'CONTAINS', 'Value': 'af-interface default', 'Message': 'MISSING EIGRP af-interface default'}], 70: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ntp authenticate', 'Message': 'MISSING ntp authenticate'}, 71: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'snmp-server enable traps snmp', 'Message': 'snmp-server enable traps snmp snmp not enabled.'}, 72: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip ssh time-out 60', 'Message': 'MISSING ip ssh timeout settings'}, 73: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip ssh authentication-retries 5', 'Message': 'MISSING ip ssh authentication-retries'}, 74: {'Scope': 'DATASET', 'Operator': 'CONTAINS', 'Value': 'v3 (noauth|auth)', 'Message': 'MISSING priv is missing from snmp-server group'}, 75: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router ospf (.*)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'no passive-interface (.*)', 'Message': 'none'}, {'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': '^*authentication message-digest.*', 'Message': 'OSPF Process <1.1> area <2.3> does not have authentication message-digest on interface <3.1>'}], 76: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'aaa accounting network', 'Message': 'none'}, 77: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ntp authentication-key', 'Message': 'MISSING ntp authentication-key'}, 78: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router ospf (.*)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': '^*no passive-interface (.*)', 'Message': 'none'}, {'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': '^*ip ospf message-digest-key ([0-9]+) md5', 'Message': 'MISSING interface <2.1> missing message-digest-key md5'}], 79: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ntp trusted-key', 'Message': 'MISSING ntp trusted-key'}, 80: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'aaa accounting system', 'Message': 'MISSING aaa accounting system'}, 81: {'Scope': 'ALL_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'ip domain[ -]name usaa.com', 'Message': 'MISSING ip domain name'}, 82: [{'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip ssh version 2', 'Message': 'none'}, {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ip ssh dh min size 2048', 'Message': 'MISSING ssh dh min 2048'}], 83: [{'Scope': 'SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'router bgp (.*)', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'neighbor (\\b\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\b) remote-as .*', 'Message': 'none'}, {'Scope': 'PREVIOUS_SUBMODE_CONFIG', 'Operator': 'MATCHES_EXPRESSION', 'Value': 'neighbor <2.1> password', 'Message': 'MISSING BGP neighbor <2.1> password'}], 84: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'aaa accounting exec', 'Message': 'MISSING aaa accounting exec'}, 85: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'ntp server 10.0.0.255 key', 'Message': 'MISSING ntp server key'}, 86: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'hostname', 'Message': 'MISSING hostname from config'}, 87: {'Scope': 'ALL_CONFIG', 'Operator': 'CONTAINS', 'Value': 'aaa accounting connection', 'Message': 'MISSING Set aaa accounting connection'}}
    data.update(dataset)
    
    violation_list = []

    ############## Single test #################
    #cfg = "./DNAC-CompMon-Data/CSW-9300-CORE.base2hq.com_run_config.txt"
    # number = 10
    #items = get_data_by_number(data, number)
    
    #for item in items:
    #    scope = item['Scope']
    #    operator = item['Operator']
    #    value = item['Value']
    #    message = item['Message']
    
    #print(f"Scope: {scope}, Operator: {operator}, Value: {value}, Message: {message}")
    #print(compare_rules(cfg, item, number))
    #print(len(data)) #88

    ########### Multiple File Test ##############
    # Set the directory to search for .txt files
    directory = './DNAC-CompMon-Data/'
    
    # Loop through each file in the directory
    #for filename in os.listdir(directory):
    #    if filename.endswith('_run_config.txt') and "temp" not in filename:
    #        path = directory + filename
    #        violation_list = (audit(path, data))
    #        compliance_report(violation_list, filename)
    compliance_run(directory, data)

if __name__ == '__main__':
    main()
    """
