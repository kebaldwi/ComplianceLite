#!/bin/bash
# Restart the Flask application by killing and re-running the gunicorn command
pkill -f "gunicorn --bind 0.0.0.0:8080 app:app"
gunicorn --bind 0.0.0.0:8080 app:app -w 1 --threads 12 &

# Pause for 2 seconds to allow the gunicorn process to restart
sleep 2