# This script ensures the test user is a superuser and staff. Safe to run multiple times.
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = os.environ.get('TEST_SUPERUSER_USERNAME', 'testuser')
EMAIL = os.environ.get('TEST_SUPERUSER_EMAIL', 'testuser@example.com')
PASSWORD = os.environ.get('TEST_SUPERUSER_PASSWORD', 'testpass123')

user, created = User.objects.get_or_create(username=USERNAME, defaults={'email': EMAIL})
if created:
    user.set_password(PASSWORD)
    print(f"Created user {USERNAME}")
else:
    print(f"User {USERNAME} already exists")

if not user.is_superuser or not user.is_staff:
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"Promoted {USERNAME} to superuser and staff.")
else:
    print(f"{USERNAME} is already superuser and staff.")
