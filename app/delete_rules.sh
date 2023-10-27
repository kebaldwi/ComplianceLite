#!/bin/bash

directory_path="$1"

# Use rm with the -rf option to recursively force delete the directory
rm -rf "$directory_path"

# Pause for 5 seconds to allow the gunicorn process to restart
sleep 5