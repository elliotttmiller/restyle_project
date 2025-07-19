from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create a superuser in production if it does not exist.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'admin'
        password = 'test123'
        email = 'admin@example.com'
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, password=password, email=email)
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created."))
        else:
            self.stdout.write(self.style.WARNING(f"Superuser '{username}' already exists.")) 