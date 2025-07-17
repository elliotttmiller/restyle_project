#!/bin/bash
set -e

python manage.py migrate
python backend/create_cloud_superuser.py
gunicorn backend.wsgi 