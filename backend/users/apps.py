from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        """Skip superuser creation in production for faster startup"""
        import os
        
        # Only create superuser in development or if explicitly requested
        if (os.environ.get('DJANGO_SETTINGS_MODULE', '').endswith('development') or 
            os.environ.get('CREATE_SUPERUSER') == 'true'):
            if os.environ.get('RUN_MAIN') != 'true':
                self.create_superuser()
    
    def create_superuser(self):
        """Create the elliotttmiller superuser if it doesn't exist"""
        try:
            from django.contrib.auth import get_user_model
            from django.db import transaction
            
            User = get_user_model()
            username = 'elliotttmiller'
            password = 'elliott'
            email = 'elliotttmiller@example.com'
            
            with transaction.atomic():
                # Check if user exists and has correct permissions
                if User.objects.filter(username=username, is_superuser=True, is_active=True).exists():
                    print(f"✅ Superuser '{username}' already exists")
                    return
                
                # Create or update user only if needed
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
                    # Update existing user only if permissions are wrong
                    user.email = email
                    user.is_staff = True
                    user.is_superuser = True
                    user.is_active = True
                    print(f"✅ Updated superuser '{username}'")
                else:
                    print(f"✅ Created superuser '{username}'")
                
                user.set_password(password)
                user.save()
                    
        except Exception as e:
            # Don't fail app startup if superuser creation fails
            print(f"⚠️  Superuser creation skipped: {e}")
            pass
