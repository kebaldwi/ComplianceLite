#!/usr/bin/env python3

####################################################################################
# project: DNAC-ComplianceMon
# module: service_email.py
# author: kebaldwi@cisco.com
# use case: Simple Check of XML audit files against configuration
# developers:
#            Gabi Zapodeanu, TME, Enterprise Networks, Cisco Systems
#            Keith Baldwin, TSA, EN Architectures, Cisco Systems
#            Bryn Pounds, PSA, WW Architectures, Cisco Systems
####################################################################################

# This section sends emails

#     ------------------------------- IMPORTS -------------------------------
import datetime
import pytz
import smtplib
import os
import os.path
import sys
import difflib
import json
import re
import time
import pytz
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
import ssl
from configuration_template import *

#     ----------------------------- DEFINITIONS -----------------------------

# This function sends an email notification.
def system_notification(ATTACHMENT):
    # Get Date and Time
    DATE, TIME = date_time(TIME_ZONE)
    # Compose the email message
    msg = MIMEMultipart()
    msg['From'] = SMTP_EMAIL
    msg['To'] = NOTIFICATION_EMAIL
    msg['Subject'] = 'DNA Center Compliance Report - ' + DATE + '.' 
    body = 'This is the report produced at ' + DATE + ' and ' + TIME + '.'
    msg.attach(MIMEText(body, 'plain'))  
    # Attach the file
    with open(ATTACHMENT, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype='pdf')
        attachment.add_header('Content-Disposition', 'attachment', filename=ATTACHMENT)
        msg.attach(attachment)
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_EMAIL, SMTP_PASS)
        server.sendmail(SMTP_EMAIL, NOTIFICATION_EMAIL, msg.as_string())
    return

def system_notification_app(directory):
    # Get Date and Time
    DATE, TIME = date_time(TIME_ZONE)
    # Compose the email message
    msg = MIMEMultipart()
    msg['From'] = SMTP_EMAIL
    msg['To'] = NOTIFICATION_EMAIL
    msg['Subject'] = 'DNA Center Compliance Report - ' + DATE + '.' 
    body = 'This is the report produced at ' + DATE + ' and ' + TIME + '.'
    msg.attach(MIMEText(body, 'plain'))  
    # Get the current date time in UTC timezone
    now_utc = datetime.datetime.now(pytz.UTC)
    # Convert to timezone
    time_zone = 'US/Eastern'
    tz = pytz.timezone(time_zone)
    now_tz = now_utc.astimezone(tz)
    # Format the date and time string
    date_str = now_tz.strftime('%m/%d/%Y').replace('/', '_')
    # Find last log file
    for filename in os.listdir(directory):
        if filename.endswith(date_str+'.pdf'):
            attachment_path = directory + filename
    # Attach the file
    with open(attachment_path, "rb") as attachment:
        # Create a MIMEBase object and set the appropriate MIME type
        mime_part = MIMEBase("application", "octet-stream")
        # Add the attachment content
        mime_part.set_payload(attachment.read())
        # Encode the attachment in base64
        encoders.encode_base64(mime_part)
        # Set the filename in the Content-Disposition header
        mime_part.add_header(
            "Content-Disposition",
            f"attachment; filename= {attachment_path.split('/')[-1]}",
        )
        # Attach the attachment to the message
        msg.attach(mime_part)    
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_EMAIL, SMTP_PASS)
        server.sendmail(SMTP_EMAIL, NOTIFICATION_EMAIL, msg.as_string())
    return

def system_message(MESSAGE):
    # Get Date and Time
    DATE, TIME = date_time(TIME_ZONE)   
    # This is the main function for testing purposes
    subject = "DNA Center Compliance System Message - " + DATE + "."
    body = MESSAGE
    message = f"Subject: {subject}\n\n{body}"
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_EMAIL, SMTP_PASS)
        server.sendmail(SMTP_EMAIL, NOTIFICATION_EMAIL, message)
    return

def date_time(TIME_ZONE):
    # Get the current date time in UTC timezone
    now_utc = datetime.datetime.now(pytz.UTC)
    # Convert to timezone
    if TIME_ZONE == '':
        time_zone = 'US/Eastern'
    else:
        time_zone = TIME_ZONE
    tz = pytz.timezone(time_zone)    
    # Check if the timezone is currently observing daylight savings time
    is_dst = bool(tz.localize(datetime.datetime.now()).dst())   
    # Convert to the specified timezone while accounting for daylight savings time
    if is_dst:
        now_tz = datetime.datetime.now(tz)
    else:
        now_tz = tz.normalize(now_utc.astimezone(tz))    
    # Format the date and time string
    date_str = now_tz.strftime('%m/%d/%Y')
    time_str = now_tz.strftime('%H:%M:%S')    
    if is_dst:
        time_str += ' (DST)'
    return date_str, time_str

#     ----------------------------- MAIN -----------------------------
# For testing and development purposes uncomment the code below

"""
message = 'this is a keith test from the system'
system_message(message)
attachment_path = './PrimeComplianceDev/COMPLIANCE_REPORT.pdf'
system_notification(attachment_path)
"""