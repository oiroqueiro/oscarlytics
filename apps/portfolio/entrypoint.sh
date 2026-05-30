#!/bin/sh

# Initialize database and static content
echo "Starting initialization process..."
python /app/init_content.py

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn --worker-tmp-dir /dev/shm --workers=2 --threads=4 --bind 0.0.0.0:8080 portfolio:portfolio
