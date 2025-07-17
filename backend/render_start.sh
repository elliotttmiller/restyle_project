#!/bin/bash
set -e

pip install -r requirements.txt
python manage.py migrate
python manage.py create_cloud_superuser.py
python manage.py collectstatic --no-input 