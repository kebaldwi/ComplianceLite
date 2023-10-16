#!/usr/bin/env python3

####################################################################################
# project: DNAC-ComplianceMon
# module: report_module.py
# author: kebaldwi@cisco.com
# use case: Simple Check of XML audit files against configuration
# developers:
#            Gabi Zapodeanu, TME, Enterprise Networks, Cisco Systems
#            Keith Baldwin, TSA, EN Architectures, Cisco Systems
#            Bryn Pounds, PSA, WW Architectures, Cisco Systems
####################################################################################

# This program is written to ingest all the XML files exported from Prime and build
# a report from the audit of configuration files.

#     ------------------------------- IMPORTS -------------------------------

import datetime
import pytz
from fpdf import FPDF
import json

#     ----------------------------- DEFINITIONS -----------------------------

# Convert a text string to a pdf report and return the pdf
def pdf_converter(DATA, DIRECTORY):
    # Define the page width and height
    PAGE_WIDTH = 8.5 * 72
    PAGE_HEIGHT = 11 * 72
    # Define the margin size
    LEFT_MARGIN = 0.25 * 72
    RIGHT_MARGIN = 0.25 * 72
    TOP_MARGIN = 0.25 * 72
    BOTTOM_MARGIN = 0.25 * 72
    # Define the font and font size
    FONT_FAMILY = "Arial"
    FONT_SIZE = 8
    # Define the PDF object
    pdf = FPDF()
    # Calculate the number of lines that can fit on one page
    lines_per_page = int((PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN) / FONT_SIZE)
    # Split the text into lines
    lines = DATA.split("\n")
    #lines = DATA
    # Loop through the lines and add them to the PDF object
    page_number = 1
    line_number = 0
    for line in lines:
        # Add a new page if necessary
        if line_number == 0:
            pdf.add_page()
            pdf.set_font(FONT_FAMILY, size=FONT_SIZE)
            pdf.set_left_margin(LEFT_MARGIN)
            pdf.set_right_margin(RIGHT_MARGIN)
            pdf.set_top_margin(TOP_MARGIN)
            pdf.set_auto_page_break(True, BOTTOM_MARGIN)
        # Add the line to the page
        pdf.cell(0, FONT_SIZE, line, ln=1)
        # Increment the line number
        line_number += 1
        # If the page is full, reset the line number and increment the page number
        if line_number == lines_per_page:
            line_number = 0
            page_number += 1
    # Get the current date time in UTC timezone
    now_utc = datetime.datetime.now(pytz.UTC)
    # Convert to timezone
    time_zone = 'US/Eastern'
    tz = pytz.timezone(time_zone)
    now_tz = now_utc.astimezone(tz)
    # Format the date and time string
    date_str = now_tz.strftime('%m/%d/%Y').replace('/', '_')
    time_str = now_tz.strftime('%H:%M:%S').replace(':', '_')
    # Define the filename for the PDF file
    FILENAME = "DNAC-COMPLIANCE-REPORT-" + date_str + ".pdf"
    report = DIRECTORY + FILENAME
    # Save the PDF file
    pdf.output(DIRECTORY + FILENAME)
    return report

# Convert an array to a JSON dictionary
def json_export(ARRAY, DIRECTORY):
    # Initialize variables for the JSON object
    compliance_report = {}
    device = {}
    tests = []
    # Parse the array and build the JSON object
    for line in ARRAY:
        # Skip empty lines
        if not line.strip():
            continue
        # Check if the line contains a compliance report header
        if ("COMPLIANCE REPORT FROM" in line):
            compliance_report["timestamp"] = line.split("FROM ")[1]
            continue
        # Check if the line contains the device name
        if ("DEVICE" in line):
            device["name"] = line.split(": ")[1]
            file_name = device["name"]
            continue
        # Check if the line contains a test result
        if line.startswith("test"):
            test = {}
            test["id"] = line.split(":")[0].strip()
            test["result"] = line.split()[3]
            if test["result"] != 'Passed':
                test["message"] = line.split(': ')[2].split('\n\n')[0]
                #test["message"] = line.split(': ')[2] #old-code
            else:
                test["message"] = ""
            # Check if the line contains an instance
            instances = []
            if ("Instances:" in line):
                test["instances"] = line.split('\n\n')[1]
            tests.append(test)
            continue
    # Add device and tests to the compliance report
    compliance_report["device"] = device
    compliance_report["tests"] = tests
    # Print the JSON object
    #print(json.dumps(compliance_report, indent=4))
    # Get the current date time in UTC timezone
    now_utc = datetime.datetime.now(pytz.UTC)
    # Convert to timezone
    time_zone = 'US/Eastern'
    tz = pytz.timezone(time_zone)
    now_tz = now_utc.astimezone(tz)
    # Format the date and time string
    date_str = now_tz.strftime('%m/%d/%Y').replace('/', '_')
    time_str = now_tz.strftime('%H:%M:%S').replace(':', '_')
    # Define the filename for the PDF file
    FILENAME = DIRECTORY + "DCR-" + file_name + "-" + date_str + ".json"
    # Save the JSON file
    with open(FILENAME, "w") as outfile:
        # Write the JSON object to the file
        json.dump(compliance_report, outfile)
    return 

#     ----------------------------- MAIN -----------------------------
# For testing and development purposes uncomment the code below

"""
text = " \
\n\n ##################################################################################################\n \
         COMPLIANCE REPORT FROM  + date_str +  + time_zone + + time_str + \n \
         DNA CENTER INTEROGATED:  + DNAC_FQDN +  @ IP ADDRESS:  + DNAC_IP + \n \
 ##################################################################################################\n \
         DEVICE:  + filename.split('_')[0] + \n \
 ##################################################################################################\n\n
 "

# Define the directory to save the PDF file in
directory = "./PrimeComplianceDev/"
pdf_converter(text,directory)
"""