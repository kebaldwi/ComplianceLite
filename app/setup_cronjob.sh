#!/bin/bash

# Retrieve the selected options from the command line arguments
schedule_type=$1
hour=$2
min=$3
day_of_week=$4

# Build the cron job commands
# typical cron settings can use [ * 1-5 1,2,3 1-10/2 = 1,3,5,7,9]
# min  hr   day  month wkday              command
# 0-59 0-23 1-31 1-12  [0-6] [sun,mon...]

# Build the cron job command based on the selected options
if [ "$schedule_type" = "daily" ]; then
    cron_command="$min $hour * * * PYTHONPATH=/usr/local/lib/python3.10/site-packages /bin/sh /app/compliancelite.sh >> /app/DNAC-CompMon-Data/System/cron.log 2>&1"
elif [ "$schedule_type" = "weekly" ]; then
    cron_command="$min $hour * * $day_of_week PYTHONPATH=/usr/local/lib/python3.10/site-packages /bin/sh /app/compliancelite.sh >> /app/DNAC-CompMon-Data/System/cron.log 2>&1"
else
    echo "Invalid schedule type selected."
    exit 1
fi

# Write the cron job command to a temporary file
echo "$cron_command" > /app/DNAC-CompMon-Data/System/cronjob

# Install the cron job from the temporary file
crontab /app/DNAC-CompMon-Data/System/cronjob

# Remove the temporary file
#rm /tmp/cronjob

# Enable the cron service
cron

# Pause for 5 seconds to allow the gunicorn process to restart
sleep 5