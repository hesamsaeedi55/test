#!/bin/bash

# Navigate to the Django project directory
cd "$(dirname "$0")/myshop2/myshop"

# Check if venv directory exists and activate it
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../../venv" ]; then
    source ../../venv/bin/activate
fi

# Collect static files to make sure our CSS and JS are available
echo "Collecting static files..."
python3 manage.py collectstatic --noinput

# Run the server
echo "Starting server..."
python3 manage.py runserver 127.0.0.1:8000