from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Set a user as staff (is_staff=True) by username.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to set as staff')

    def handle(self, *args, **options):
        username = options['username']
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f"User '{username}' set as staff (is_staff=True)."))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User '{username}' does not exist.")) 