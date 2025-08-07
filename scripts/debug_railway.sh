#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--- [DEBUG] STARTING RAILWAY STARTUP SCRIPT ---"

echo "--- [DEBUG] 1. WAITING FOR DATABASE ---"
python wait_for_postgres.py
echo "--- [DEBUG] Database is responsive. ---"

echo "--- [DEBUG] 2. RUNNING DATABASE MIGRATIONS ---"
python manage.py migrate --noinput
echo "--- [DEBUG] Database migrations completed successfully. ---"

echo "--- [DEBUG] 3. COLLECTING STATIC FILES ---"
python manage.py collectstatic --noinput
echo "--- [DEBUG] Static files collected successfully. ---"

echo "--- [DEBUG] 4. STARTING GUNICORN SERVER ---"
gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --log-level debug
echo "--- [DEBUG] Gunicorn command executed. If you see this, it may have exited unexpectedly. ---"
