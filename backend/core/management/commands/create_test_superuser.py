import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates or updates a test superuser for the comprehensive test suite.'

    def handle(self, *args, **options):
        username = os.environ.get("TEST_USER", "testuser")
        password = os.environ.get("TEST_PASS", "testpass1234")
        email = f"{username}@example.com"

        if not username or not password:
            self.stdout.write(self.style.ERROR("TEST_USER and TEST_PASS environment variables must be set."))
            return

        # get_or_create returns a tuple (object, created_boolean)
        user, created = User.objects.get_or_create(username=username)
        
        if created:
            user.email = email
            self.stdout.write(self.style.SUCCESS(f"Test user '{username}' created."))
        else:
            self.stdout.write(self.style.WARNING(f"Test user '{username}' already exists. Ensuring superuser status."))

        # Set password and superuser privileges
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(self.style.SUCCESS(f"Successfully configured '{username}' as a superuser."))
