#!/bin/sh
set -e

echo "Starting Django application..."

# Set production settings
export DJANGO_SETTINGS_MODULE=backend.settings.prod

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create/update superuser
echo "Ensuring production superuser exists and has correct password/flags..."
python manage.py create_prod_superuser

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn with proper configuration for Railway
echo "Starting Gunicorn server..."
exec gunicorn backend.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info 