# Compliance Lite
Using Cisco Catalyst (DNA) Center for Configuration Monitoring and Compliance and sending notifications as incidents via email.

This repo will use xml formatted compliance rules with Cisco Catalyst (DNA) Center to detect and mitigate unauthorized, or non-compliant configuration changes and notify via Email.

This repo is based on ConfigMon-DNAC by Gabi Z

Compliance additions by Keith Baldwin & Bryn Pounds.

## The Challenge: 
 - 70% of policy violations are due to user errors
 - Configuration drifting
 - non compliant code
 - compliancy audits

## The Goal: 
 - Detect and alert on all network configuration changes
 - Report on Non Complaint configurations

## The Solution:
 - Integration between Cisco Catalyst (DNA) Center and this tool.
 - The application may run on demand via web UI, CLI or via CRON scheduled job.

## Workflow:
 - Collect network devices running configurations using the Cisco DNA Center Command Runner APIs
 - Create a local folder with all the running configurations
 - If the device is new, add the configuration to the local folder
 - If device is known, check for configuration changes
 - If a change occurred, identify who made the change, the device name, physical location and device health
 - Identify what changed and the relevant section of the configuration
 - Inspect against provided compliance policies:
   - no logging configuration changes, 
   - no access control lists configuration,
   - prevent IPv4 duplicate addresses
   - check for non compliant configurations using xml audits from Prime Compliance Module

## The Results: 
 - Non compliant configuration changes are notified and reported
 - Troubleshooting assistance by providing a real time view of all device configuration changes
 
## Setup and Configuration
 - The requirements.txt file include all the Python libraries needed for this application
 - This application requires:
   - Cisco DNA Center
 - The config.py is the only file needed to be customized to match your environment may be modified via UI in container or via system_setup.py

 ## To run this application as a Container in Docker follow these steps:
 - Download the entire repo to your system using a git pull
 - Ensure Docker is installed
 - Change to the root of the files where the README.md file is
 - Use the following commands:
   1. docker build -t my-app .
   2. docker run -d -p 8080:8080 --name ComplianceLite my-app 
   3. browse to localhost:8080 in a browser

## Roadmap:
 - Automate roll back of non-compliant changes
 - Approval process for all compliant configuration changes
 - Continue to Build a web based dashboard
 - Create additional compliance checks
 - Create northbound APIs to provide additional services like - configurations search, reporting, service-now integration

## Future Setup Configurations and Roadmap
 - In the future this application will include:
   - IOS XE devices configured for NETCONF and RESTCONF
   - Cisco Webex Teams account
   - ServiceNow developer account
