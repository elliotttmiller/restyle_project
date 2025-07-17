#!/bin/bash
set -e

pip install -r requirements.txt
python manage.py test
python manage.py migrate
python create_cloud_superuser.py
python manage.py collectstatic --no-input
gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT 