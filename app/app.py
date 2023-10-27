from flask import Flask, render_template, send_from_directory, request, url_for, flash, redirect
import json
import requests
import time
import datetime
import subprocess
import shutil
import pytz
import zipfile
import io
import re
import os
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from subprocess import PIPE
from configuration_template import DNAC_URL, DNAC_PASS, DNAC_USER, SMTP_EMAIL, SMTP_PASS, SMTP_SERVER, SMTP_PORT, SMTP_FLAG, NOTIFICATION_EMAIL
from compliance_mon import *
from difference_engine import *
from system_setup import *
from version import *
from rule_manager import *
from compliance_summary import *
load_dotenv()

try:
    from API import (app,
                     api,
                     HealthController,docs,
                     ComplianceLite,
                     WeatherController,
                     )
except Exception as e:
    print("Modules are Missing : {} ".format(e))
    
messages=["howdy"]

os_setup()
data_library(CONFIG_PATH,CONFIG_STORE,REPORT_STORE,JSON_STORE,SYSTEM_STORE)

if os.path.isfile('/app/DNAC-CompMon-Data/System/cronjob'):
    # Run the shell script
    subprocess.run(['bash', 'restart_cronjob.sh'])

@app.route("/")
def home():
    my_var = "Welcome to DNA Center Compliance Lite"
    result = subprocess.run(["ls", "-l", "/app/DNAC-CompMon-Data/Reports", "/dev/null"], stdout=PIPE, stderr=PIPE)
    contents = result.stdout.decode('utf8')
    return render_template("home.html", message = contents.split("total")[1], version=version)

@app.route("/about")
def about():
    return render_template("about.html", version=version)

@app.route("/system_resets", methods=['GET', 'POST'])
#modified to use existing code
def system_reset():
    global CONFIG_PATH
    global CONFIG_STORE
    global REPORT_STORE
    global JSON_STORE
    global SYSTEM_STORE
    if request.method == 'POST':
        #reset system settings to default
        default_system_app(CONFIG_PATH, CONFIG_STORE, REPORT_STORE, JSON_STORE, SYSTEM_STORE)
        # Execute the shell script to restart the Flask application
        # Add a two-second pause
        time.sleep(2)
        subprocess.run(['bash', 'restart_app.sh'])
        import_status = PRIME_import_status()
        if import_status != "Not Imported":
            # Delete prime compliance rules
            directory_path = '/app/PrimeComplianceChecks'
            directories = [name for name in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, name))]
            for subdirectory in directories:
                subdirectory_path = os.path.join(directory_path, subdirectory)
            # Call the bash script to shut down and delete the cron job
            subprocess.run(['bash', 'delete_rules.sh', subdirectory_path])
        if os.path.isfile('/app/DNAC-CompMon-Data/System/cronjob'):
            # Run the shell script
            subprocess.run(['bash', 'delete_cronjob.sh'])
        # Add a two-second pause
        time.sleep(2)
        return redirect(url_for('home'))
    return render_template("system_resets.html", version=version)

@app.route("/configure_system", methods=['GET', 'POST'])
#modified to use existing code
def configure_system():
    global DNAC_IP
    global DNAC_USER
    global DNAC_PASS
    global DNAC_URL
    if request.method == 'POST':
        DNAC_IP = request.form['ip_address']
        DNAC_USER = request.form['username']
        DNAC_PASS = request.form['password']
        # Define the path to the Python file to update
        PATH = "/app/configuration_template.py"
        if not DNAC_IP:
            flash('IP Address is required!')
        elif not DNAC_USER:
            flash('Username is required!')        
        elif not DNAC_PASS:
            flash('Password is required!')
        else:
            DNAC_setup_app(PATH,DNAC_IP,DNAC_USER,DNAC_PASS)
            # Add a two-second pause
            time.sleep(2)
            subprocess.run(['bash', 'restart_app.sh'])
            # Add a two-second pause
            time.sleep(2)
            return redirect(url_for('status'))    
    return render_template("configure_system.html",ip_address=DNAC_IP,username=DNAC_USER,password=DNAC_PASS, version=version)

@app.route("/configure_email", methods=['GET', 'POST'])
#modified to use existing code
def configure_email():
    global SMTP_EMAIL
    global SMTP_PASS
    global SMTP_SERVER
    global SMTP_PORT
    global SMTP_FLAG
    global NOTIFICATION_EMAIL
    if request.method == 'POST':
        SMTP_EMAIL = request.form['email_address']
        SMTP_PASS = request.form['email_password']
        SMTP_SERVER = request.form['smtp_server']
        SMTP_PORT = request.form['smtp_port']
        NOTIFICATION_EMAIL = request.form['email_recipient']
        # Define the path to the Python file to update
        PATH = "/app/configuration_template.py"
        if not SMTP_EMAIL:
            flash('Email Address is required!')
        elif not SMTP_PASS:
            flash('Email Password is required!')        
        elif not SMTP_SERVER:
            flash('SMTP Server is required!')
        elif not SMTP_PORT:
            flash('SMTP Port is required!')
        elif not SMTP_PORT:
            flash('SMTP Port is required!')
        elif not NOTIFICATION_EMAIL:
            flash('Email Recipient is required!')
        else:
            SMTP_FLAG = True
            SMTP_setup_app(PATH,SMTP_EMAIL,SMTP_PASS,SMTP_SERVER,SMTP_PORT,SMTP_FLAG,NOTIFICATION_EMAIL)
            # Add a two-second pause
            time.sleep(2)
            subprocess.run(['bash', 'restart_app.sh'])
            # Add a two-second pause
            time.sleep(2)
            return redirect(url_for('status'))    
    return render_template("configure_email.html",email_address=SMTP_EMAIL,email_password=SMTP_PASS,smtp_server=SMTP_SERVER,smtp_port=SMTP_PORT,email_recipient=NOTIFICATION_EMAIL, version=version)

@app.route("/configure_time", methods=['GET', 'POST'])
#modified to use existing code
def configure_tzone():
    global TIME_ZONE
    if request.method == 'POST':
        TIME_ZONE = request.form['time_zone']
        # Define the path to the Python file to update
        PATH = "/app/configuration_template.py"
        if not TIME_ZONE:
            flash('Time Zone is required!')
        else:
            TZONE_setup_app(PATH,TIME_ZONE)
            # Add a two-second pause
            time.sleep(2)
            subprocess.run(['bash', 'restart_app.sh'])
            # Add a two-second pause
            time.sleep(2)
            return redirect(url_for('status'))    
    time_zones = pytz.all_timezones
    return render_template("configure_time.html",time_zone=TIME_ZONE,time_zones=time_zones, version=version)

@app.route("/configure_rules", methods=['GET', 'POST'])
#modified to use existing code
def configure_rules():
    if request.method == 'POST':
        # Get the uploaded file
        uploaded_file = request.files['file']
        compliance_files = os.path.join(CONFIG_PATH, COMPLIANCE_STORE)
        folder_name = os.path.splitext(uploaded_file.filename)[0]
        uploaded_path = os.path.join(CONFIG_PATH, COMPLIANCE_STORE, folder_name)
        #PRIME_import_app(CONFIG_PATH, COMPLIANCE_STORE, UPLOADED_FILE) 
        # Create a folder to extract the contents to
        if uploaded_file.filename.endswith('.zip'):
            if not os.path.exists(compliance_files):
                os.makedirs(compliance_files)        
            if not os.path.exists(uploaded_path):
                # Extract the contents of the zip file to the folder
                os.mkdir(uploaded_path)        
                with zipfile.ZipFile(io.BytesIO(uploaded_file.read())) as zip_ref:
                    zip_ref.extractall(compliance_files)
                outcome = "SUCCESS"
                import_status = PRIME_import_status()
                return render_template("configure_rules.html", import_status=import_status, version=version)
            else:
                outcome = "FAILURE"
        else:
            outcome = "FAILURE"
    import_status = PRIME_import_status()
    return render_template("configure_rules.html", import_status=import_status, version=version)

@app.route('/rule_delete', methods=['POST'])
def rule_delete():
    directory_path = '/app/PrimeComplianceChecks'
    directories = [name for name in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, name))]
    for subdirectory in directories:
        subdirectory_path = os.path.join(directory_path, subdirectory)
    # Call the bash script to shut down and delete the cron job
    subprocess.run(['bash', 'delete_rules.sh', subdirectory_path]) 
    # Redirect to a success page or display a success message
    return redirect(url_for('status')) 

@app.route("/report", methods=['GET', 'POST'])
#modified to use existing code
def serve_report():
    if request.method == 'POST':
        comp_main()
        return redirect('/') 
    message = "Reports..."
    result = subprocess.run(["ls", "-l", "/app/DNAC-CompMon-Data/Reports/", "/dev/null"], stdout=PIPE, stderr=PIPE)
    contents = result.stdout.decode('utf8')
    dnac_status = DNAC_status_app(DNAC_IP,DNAC_USER,DNAC_PASS)
    import_status = PRIME_import_status()
    if dnac_status != "Connected" and import_status == "Not Imported":
        disable_service = "disable"
    else:
        disable_service = "enable"    
    return render_template('report.html', message=message, reports=contents.split("total")[1],disable_service=disable_service, version=version)

@app.route('/download/<path:filename>')
def download_file(filename):
    # specify the path to the external directory
    if '.pdf' in filename:
        external_directory = '/app/DNAC-CompMon-Data/Reports/'
    elif '.xml' in filename:
        parent_directory = "/app/PrimeComplianceChecks"
        subdirectory = PRIME_import_status()
        # Create the full path by joining the parent directory, subdirectory, and filename
        external_directory = os.path.join(parent_directory, subdirectory)
    elif '.txt' in filename:
        external_directory = '/app/DNAC-CompMon-Data/Configs/'
    # use send_from_directory to serve the file
    return send_from_directory(external_directory, filename, as_attachment=True)

@app.route("/scheduler", methods=['GET', 'POST'])
def scheduler_app():
    # Check if the cron job is configured
    try:
        result = subprocess.run(['service', 'cron', 'status'], stdout=subprocess.PIPE)
        status = result.stdout.decode('utf-8').strip()
        # If the cron service is running, get the next scheduled run time
        if 'not' not in status:
            result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE)
            content = result.stdout.decode('utf-8')
            # Check if the cron job runs every day or at a specific day and time
            if '* * *' in content:
                schedule = 'Daily'
                match = re.match(r'^(\d{1,2})\s+(\d{1,2})', content)
                if match:
                    # Display the hours and minutes
                    read_hours = match.group(2)
                    read_minutes = match.group(1)
                next_run_time_str = read_hours + ":" + read_minutes + " hrs"
            else:
                schedule = 'Weekly'
                match = re.match(r'^(\d{1,2})\s+(\d{1,2}).*(mon|tue|wed|thu|fri|sat|sun)', content)
                if match:
                    # Display the hours and minutes
                    read_hours = match.group(2)
                    read_minutes = match.group(1)
                    read_day = match.group(3)
                    display_day = short_to_long(read_day)
                next_run_time_str = read_hours + ":" + read_minutes + " hrs on " + display_day
            # Pass the status, schedule, and next run time to the HTML template
            message = 'Service Running: ' + schedule + " @ " + next_run_time_str
        else:
            message = 'Service Not Running: '
    except FileNotFoundError:
        message = 'Service Not Configured: '
    time_options = []
    for hour in range(24):
        for minute in range(0,60,15):
            time_options.append(f'{hour:02d}:{minute:02d}')
    days_of_week = []
    today = datetime.date.today()
    for i in range(7):
        day = today + datetime.timedelta(days=i)
        days_of_week.append(day.strftime('%A'))
    if request.method == 'POST':
        schedule_type = request.form.get('schedule_type')
        if schedule_type == 'daily':
            time_of_day = request.form.get('daily_time_of_day')
            hour_output, minute_output = time_of_day.split(":")
            truncated_day = "none"
            message = 'you selected: ' + schedule_type + " and " + time_of_day + "HRS every day."
            # Execute the shell script to set up the cron job
            subprocess.run(['bash', 'setup_cronjob.sh', schedule_type, hour_output, minute_output, truncated_day])
            # Add a three-second pause
            time.sleep(3)
        elif schedule_type == 'weekly':
            time_of_day = request.form.get('weekly_time_of_day')
            day_of_week = request.form.get('day_of_week')
            hour_output, minute_output = time_of_day.split(":")
            truncated_day = day_of_week[:3].lower()
            message = 'Service Created: ' + schedule_type + " " + time_of_day + " hrs every " + day_of_week
            # Execute the shell script to set up the cron job
            subprocess.run(['bash', 'setup_cronjob.sh', schedule_type, hour_output, minute_output, truncated_day])
            # Add a three-second pause
            time.sleep(3)
    dnac_status = DNAC_status_app(DNAC_IP,DNAC_USER,DNAC_PASS)
    import_status = PRIME_import_status()
    if dnac_status != "Connected" and import_status == "Not Imported":
        disable_service = "disable"
    else:
        disable_service = "enable"
    return render_template("scheduler.html",time_options=time_options,days_of_week=days_of_week,message=message,disable_service=disable_service, version=version)

@app.route('/delete', methods=['POST'])
def delete():
    # Call the bash script to shut down and delete the cron job
    subprocess.run(['bash', 'delete_cronjob.sh']) 
    # Redirect to a success page or display a success message
    return redirect(url_for('status')) 

@app.route('/devices')
def device_list():
    result = subprocess.run(["ls", "-l", "/app/DNAC-CompMon-Data/Configs/", "/dev/null"], stdout=PIPE, stderr=PIPE)
    content = result.stdout.decode('utf8')    
    return render_template('devices.html', content=content, version=version)

# Define a route to display the table of XML file information
@app.route("/rule_manager")
def display_xml_files():
    # Get a list of all XML files in the directory
    parent_directory = "/app/PrimeComplianceChecks"
    subdirectory = PRIME_import_status()
    if subdirectory == "Not Imported":
        return redirect('configure_rules')
    file_path = os.path.join(parent_directory, subdirectory)
    xml_files = [f for f in os.listdir(file_path) if f.endswith(".xml")]
    # Parse each XML file and store the title, description, and filename in a list of dictionaries
    xml_data = []
    for xml_file in xml_files:
        xml_path = os.path.join(file_path, xml_file)
        title, description = parse_xml_file(xml_path)
        xml_data.append({"title": title, "description": description, "filename": xml_file})
    # Render the template with the list of XML file information
    return render_template("rule_manager.html", rules=subdirectory, xml_data=xml_data, version=version)

# Define a route to delete an XML file
@app.route("/delete_rule", methods=["POST"])
def delete_xml_file():
    # Get XML directory
    parent_directory = "/app/PrimeComplianceChecks"
    subdirectory = PRIME_import_status()
    file_path = os.path.join(parent_directory, subdirectory)
    # Get the filename of the XML file to delete from the form data
    filename = request.form["filename"]
    # Delete the XML file from the directory
    os.remove(os.path.join(file_path, filename))
    # Redirect back to the main page
    return redirect("/")

@app.route("/status")
def status():
    file1 = open('/app/configuration_template.py', 'r')
    contents = file1.read()
    file1.close()
    url = 'http://localhost:8080/health_check'
    response = requests.get(url)
    our_response_content = response.content.decode('utf8')
    proper_json_response = json.loads(our_response_content)
    status = DNAC_status_app(DNAC_IP,DNAC_USER,DNAC_PASS)
    smtp_status = SMTP_status_app(SMTP_EMAIL,SMTP_PASS,SMTP_SERVER,SMTP_PORT)
    import_status = PRIME_import_status()
    service_status = scheduler_status_app()
    return render_template("status.html", testing=proper_json_response, status=status, smtp_status=smtp_status, time_zone=TIME_ZONE, import_status=import_status, service_status=service_status, contents=contents, version=version)

config_directory = os.path.join(APP_DIRECTORY, CONFIG_STORE)

@app.route('/summary_report')
def summary_report():
    json_directory = os.path.join(APP_DIRECTORY, JSON_STORE)
    recent_filenames = get_recent_files(json_directory)
    data = []
    total_passed = 0
    total_failed = 0 
    for filename in recent_filenames:
        if ".json" in filename:
            with open(os.path.join(json_directory, filename)) as f:
                json_data = json.load(f)
                hostname = json_data['device']['name']
                timestamp_str = json_data['timestamp']
                date_str, time_str = timestamp_str.split(' ')[0], timestamp_str.split(' ')[-1]
                date = date_str + ' ' + time_str
                tests = json_data['tests']
                passed_tests = sum(1 for test in tests if test['result'] == 'Passed')
                failed_tests = sum(1 for test in tests if test['result'] != 'Passed')
                total_passed = total_passed + passed_tests
                total_failed = total_failed + failed_tests
                total_tests = len(tests)
                data.append((hostname, date, passed_tests, failed_tests, total_tests))
    return render_template('summary_report.html', total_passed=total_passed, total_failed=total_failed, data=data, version=version)    

@app.route("/weather")
def weather():
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }
    
    json_data = {
        'city': 'Overland Park',
        'zip': '66085',
    }
    
    response = requests.post('http://localhost:8080/check_weather', headers=headers, json=json_data)    
    #url = 'http://192.241.187.136/data/2.5/weather?zip=66085,us&appid=11a1aac6bc7d01ea13f0d2a8e78c227e'
    #my_response = requests.get(url)
    our_response_content = response.content.decode('utf8')
    proper_json_response = json.loads(our_response_content)
    return render_template("weather.html", message="HOWDY", testing=proper_json_response, version=version)

api.add_resource(HealthController, '/health_check')
docs.register(HealthController)

api.add_resource(ComplianceLite, '/Compliance_Lite')
docs.register(ComplianceLite)

api.add_resource(WeatherController, '/check_weather')
docs.register(WeatherController)

if __name__ == '__main__':
    app.run(threaded=True)