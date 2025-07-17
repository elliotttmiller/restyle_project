#!/bin/bash
set -e

python manage.py test
python manage.py migrate
python create_cloud_superuser.py
gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT 