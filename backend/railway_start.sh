#!/bin/sh
set -e

echo "Starting Django application..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Force admin user to be staff, superuser, active, and set password
echo "Ensuring production superuser exists and has correct password/flags..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'}); u.is_staff = True; u.is_superuser = True; u.is_active = True; u.set_password('test123'); u.save(); print('Admin user updated:', u.username, u.is_staff, u.is_superuser, u.is_active)"

# Diagnostic: Print all users and their flags
echo "Printing all users and their flags for debugging..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('All users:'); [print(u.username, u.is_staff, u.is_superuser, u.is_active) for u in User.objects.all()]"

# Create superuser if not exists
echo "Ensuring production superuser exists..."
python manage.py create_prod_superuser

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn with proper configuration for Railway
echo "Starting Gunicorn server..."
gunicorn backend.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info 