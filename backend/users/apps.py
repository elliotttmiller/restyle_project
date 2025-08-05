from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        """Create or update the superuser on app startup"""
        # Only run this once during startup, not during migrations
        import os
        if os.environ.get('RUN_MAIN') != 'true':
            self.create_superuser()
    
    def create_superuser(self):
        """Create or update the elliotttmiller superuser"""
        try:
            from django.contrib.auth import get_user_model
            from django.db import transaction
            
            User = get_user_model()
            username = 'elliotttmiller'
            password = 'elliott'
            email = 'elliotttmiller@example.com'
            
            with transaction.atomic():
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': email,
                        'is_staff': True,
                        'is_superuser': True,
                        'is_active': True,
                    }
                )
                
                if not created:
                    # Update existing user to ensure correct settings
                    user.email = email
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_active = True
                    user.set_password(password)
                    user.save()
                    print(f"Updated superuser '{username}' with correct permissions")
                else:
                    user.set_password(password)
                    user.save()
                    print(f"Created superuser '{username}' successfully")
                    
        except Exception as e:
            # Don't fail app startup if superuser creation fails
            print(f"Warning: Could not create/update superuser: {e}")
            pass
