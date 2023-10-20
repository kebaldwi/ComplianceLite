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
from subprocess import PIPE
from dotenv import load_dotenv
from configuration_template import DNAC_URL, DNAC_PASS, DNAC_USER, SMTP_EMAIL, SMTP_PASS, SMTP_SERVER, SMTP_PORT, SMTP_FLAG, NOTIFICATION_EMAIL
from compliance_mon import *
from difference_engine import *
from system_setup import *
from version import *
load_dotenv()

try:
    from API import (app,
                     api,
                     HealthController,docs,
                     DNACenterCompliance,
                     WeatherController,
                     DNACTokenController,
                     get_all_device_infoController,
                     get_device_infoController,
                     delete_deviceController,
                     get_project_idController,
                     get_project_infoController,
                     create_commit_templateController,
                     commit_templateController,
                     update_commit_templateController,
                     upload_templateController,
                     delete_templateController,
                     get_all_template_infoController,
                     get_template_name_infoController,
                     get_template_idController,
                     get_template_id_versionController,
                     get_template_id_versionController,
                     deploy_templateController,
                     check_template_deployment_statusController,
                     get_client_infoController,
                     locate_client_ipController,
                     get_device_id_nameController,
                     get_device_statusController,
                     get_device_management_ipController,
                     get_device_id_snController,
                     get_device_locationController,
                     create_siteController,
                     get_site_idController,
                     create_buildingController,
                     get_building_idController,
                     create_floorController,
                     get_floor_idController,
                     assign_device_sn_buildingController,
                     assign_device_name_buildingController,
                     get_geo_infoController,
                     sync_deviceController,
                     check_task_id_statusController,
                     check_task_id_outputController,
                     create_path_traceController,
                     get_path_trace_infoController,
                     check_ipv4_network_interfaceController,
                     get_device_info_ipController,
                     get_legit_cli_command_runnerController,
                     get_content_file_idController,
                     get_output_command_runnerController,
                     get_all_configsController,
                     get_device_configController,
                     check_ipv4_addressController,
                     check_ipv4_address_configsController,
                     check_ipv4_duplicateController,
                     get_device_healthController,
                     pnp_get_device_countController,
                     pnp_get_device_listController,
                     pnp_claim_ap_siteController,
                     pnp_delete_provisioned_deviceController,
                     pnp_get_device_infoController,
                     get_physical_topologyController
                     )
except Exception as e:
    print("Modules are Missing : {} ".format(e))
    
messages=["howdy"]

os_setup()
data_library(CONFIG_PATH,CONFIG_STORE,REPORT_STORE,JSON_STORE,SYSTEM_STORE)

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
                return render_template("configure_rules.html")
            else:
                outcome = "FAILURE"
        else:
            outcome = "FAILURE"
    return render_template("configure_rules.html", version=version)

@app.route("/report", methods=['GET', 'POST'])
#modified to use existing code
def serve_report():
    if request.method == 'POST':
        comp_main()
        return redirect('/') 
    message = "Reports..."
    result = subprocess.run(["ls", "-l", "/app/DNAC-CompMon-Data/Reports/", "/dev/null"], stdout=PIPE, stderr=PIPE)
    contents = result.stdout.decode('utf8')
    return render_template('report.html', message=message, reports=contents.split("total")[1], version=version)

@app.route('/download/<path:filename>')
def download_file(filename):
    # specify the path to the external directory
    external_directory = '/app/DNAC-CompMon-Data/Reports/'
    # use send_from_directory to serve the file
    return send_from_directory(external_directory, filename, as_attachment=True)

@app.route("/scheduler", methods=['GET', 'POST'])
def scheduler_app():
    message = " "
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
    return render_template("scheduler.html",time_options=time_options,days_of_week=days_of_week,message=message, version=version)

@app.route("/status")
def status():
    file1 = open('/app/configuration_template.py', 'r')
    contents = file1.read()
    file1.close()
    url = 'http://localhost:8080/health_check'
    response = requests.get(url)
    our_response_content = response.content.decode('utf8')
    proper_json_response = json.loads(our_response_content)
    return render_template("status.html", testing=proper_json_response, DNAC_URL=DNAC_URL, DNAC_USER=DNAC_USER, messages=messages, contents=contents, version=version)

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

api.add_resource(DNACenterCompliance, '/DNA_Center_Compliance_Lite')
docs.register(DNACenterCompliance)

api.add_resource(WeatherController, '/check_weather')
docs.register(WeatherController)

api.add_resource(DNACTokenController, '/get_dnac_token')
docs.register(DNACTokenController)

api.add_resource(get_all_device_infoController, '/get_all_device_info')
docs.register(get_all_device_infoController)

api.add_resource(get_device_infoController, '/get_device_info')
docs.register(get_device_infoController)

api.add_resource(delete_deviceController, '/delete_device')
docs.register(delete_deviceController)

api.add_resource(get_project_idController, '/get_project_id')
docs.register(get_project_idController)

api.add_resource(get_project_infoController, '/get_project_info')
docs.register(get_project_infoController)

api.add_resource(create_commit_templateController, '/create_commit_template')
docs.register(create_commit_templateController)

api.add_resource(commit_templateController, '/commit_template')
docs.register(commit_templateController)

api.add_resource(update_commit_templateController, '/update_commit_template')
docs.register(update_commit_templateController)

api.add_resource(upload_templateController, '/upload_template')
docs.register(upload_templateController)

api.add_resource(delete_templateController, '/delete_template')
docs.register(delete_templateController)

api.add_resource(get_all_template_infoController, '/get_all_template_info')
docs.register(get_all_template_infoController)

api.add_resource(get_template_name_infoController, '/get_template_name_info')
docs.register(get_template_name_infoController)

api.add_resource(get_template_idController, '/get_template_id')
docs.register(get_template_idController)

api.add_resource(get_template_id_versionController, '/get_template_id_version')
docs.register(get_template_id_versionController)

api.add_resource(deploy_templateController, '/deploy_template')
docs.register(deploy_templateController)

api.add_resource(check_template_deployment_statusController, '/check_template_deployment_status')
docs.register(check_template_deployment_statusController)

api.add_resource(get_client_infoController, '/get_client_info')
docs.register(get_client_infoController)

api.add_resource(locate_client_ipController, '/locate_client_ip')
docs.register(locate_client_ipController)

api.add_resource(get_device_id_nameController, '/get_device_id_name')
docs.register(get_device_id_nameController)

api.add_resource(get_device_statusController, '/get_device_status')
docs.register(get_device_statusController)

api.add_resource(get_device_management_ipController, '/get_device_management_ip')
docs.register(get_device_management_ipController)

api.add_resource(get_device_id_snController, '/get_device_id_sn')
docs.register(get_device_id_snController)

api.add_resource(get_device_locationController, '/get_device_location')
docs.register(get_device_locationController)

api.add_resource(create_siteController, '/create_site')
docs.register(create_siteController)

api.add_resource(get_site_idController, '/get_site_id')
docs.register(get_site_idController)

api.add_resource(create_buildingController, '/create_building')
docs.register(create_buildingController)

api.add_resource(get_building_idController, '/get_building_id')
docs.register(get_building_idController)

api.add_resource(create_floorController, '/create_floor')
docs.register(create_floorController)

api.add_resource(get_floor_idController, '/get_floor_id')
docs.register(get_floor_idController)

api.add_resource(assign_device_sn_buildingController, '/assign_device_sn_building')
docs.register(assign_device_sn_buildingController)

api.add_resource(assign_device_name_buildingController, '/assign_device_name_building')
docs.register(assign_device_name_buildingController)

api.add_resource(get_geo_infoController, '/get_geo_info')
docs.register(get_geo_infoController)

api.add_resource(sync_deviceController, '/sync_device')
docs.register(sync_deviceController)

api.add_resource(check_task_id_statusController, '/check_task_id_status')
docs.register(check_task_id_statusController)

api.add_resource(check_task_id_outputController, '/check_task_id_output')
docs.register(check_task_id_outputController)

api.add_resource(create_path_traceController, '/create_path_trace')
docs.register(create_path_traceController)

api.add_resource(get_path_trace_infoController, '/get_path_trace_info')
docs.register(get_path_trace_infoController)

api.add_resource(check_ipv4_network_interfaceController, '/check_ipv4_network_interface')
docs.register(check_ipv4_network_interfaceController)

api.add_resource(get_device_info_ipController, '/get_device_info_ip')
docs.register(get_device_info_ipController)

api.add_resource(get_legit_cli_command_runnerController, '/get_legit_cli_command_runner')
docs.register(get_legit_cli_command_runnerController)

api.add_resource(get_content_file_idController, '/get_content_file_id')
docs.register(get_content_file_idController)

api.add_resource(get_output_command_runnerController, '/get_output_command_runner')
docs.register(get_output_command_runnerController)

api.add_resource(get_all_configsController, '/get_all_configs')
docs.register(get_all_configsController)

api.add_resource(get_device_configController, '/get_device_config')
docs.register(get_device_configController)

api.add_resource(check_ipv4_addressController, '/check_ipv4_address')
docs.register(check_ipv4_addressController)

api.add_resource(check_ipv4_address_configsController, '/check_ipv4_address_configs')
docs.register(check_ipv4_address_configsController)

api.add_resource(check_ipv4_duplicateController, '/check_ipv4_duplicate')
docs.register(check_ipv4_duplicateController)

api.add_resource(get_device_healthController, '/get_device_health')
docs.register(get_device_healthController)

api.add_resource(pnp_get_device_countController, '/pnp_get_device_count')
docs.register(pnp_get_device_countController)

api.add_resource(pnp_get_device_listController, '/pnp_get_device_list')
docs.register(pnp_get_device_listController)

api.add_resource(pnp_claim_ap_siteController, '/pnp_claim_ap_site')
docs.register(pnp_claim_ap_siteController)

api.add_resource(pnp_delete_provisioned_deviceController, '/pnp_delete_provisioned_device')
docs.register(pnp_delete_provisioned_deviceController)

api.add_resource(pnp_get_device_infoController, '/pnp_get_device_info')
docs.register(pnp_get_device_infoController)

api.add_resource(get_physical_topologyController, '/get_physical_topology')
docs.register(get_physical_topologyController)

if __name__ == '__main__':
    app.run(threaded=True)