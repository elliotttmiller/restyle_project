from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create a superuser in production if it does not exist.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'elliotttmiller'
        password = 'elliott'
        email = 'elliotttmiller@example.com'
        
        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                }
            )
            
            # Always update password and permissions
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Superuser '{username}' created successfully.")
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Superuser '{username}' updated successfully.")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error creating/updating superuser: {e}")
            ) 