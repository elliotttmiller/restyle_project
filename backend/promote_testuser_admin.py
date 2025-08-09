from django.contrib.auth import get_user_model

User = get_user_model()
try:
    u = User.objects.get(username="testuser")
    u.is_staff = True
    u.is_superuser = True
    u.save()
    print("✅ testuser promoted to admin (is_staff=True, is_superuser=True)")
except User.DoesNotExist:
    print("❌ testuser does not exist. Please register the user first.")
