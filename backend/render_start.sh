#!/bin/bash
set -e

python manage.py test
python manage.py migrate
python create_cloud_superuser.py
gunicorn backend.wsgi 