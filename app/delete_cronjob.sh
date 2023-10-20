#!/bin/bash

# Remove the cron job
crontab -l | grep -v "your_cron_job" | crontab -

# Stop the cron service
service cron stop

# Remove the temporary file
rm /app/DNAC-CompMon-Data/System/cronjob

# Pause for 5 seconds to allow the gunicorn process to restart
sleep 5