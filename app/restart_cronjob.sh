#!/bin/bash

# Install the cron job from the temporary file
crontab /app/DNAC-CompMon-Data/System/cronjob

# Remove the temporary file
#rm /app/DNAC-CompMon-Data/System/cronjob

# Enable the cron service
service cron start

# Pause for 5 seconds to allow the gunicorn process to restart
sleep 5